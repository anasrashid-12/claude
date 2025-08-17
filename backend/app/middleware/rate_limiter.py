import os
import logging
from typing import Dict, Iterable, Optional, Tuple, Set

import time
import jwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger("rate_limiter")


# One atomic script that:
#  - optionally dedupes via Idempotency-Key (SET with TTL)
#  - enforces two sliding-window ZSETs (burst + sustained)
#  - returns remaining (min across buckets) and TTL (max until reset across buckets)
LUA_DUAL_BUCKET = r"""
-- KEYS:
-- 1: key_burst (ZSET)
-- 2: key_sust  (ZSET)
-- 3: key_dedupe (SET)  [optional, may be "" to skip]
-- ARGV:
-- 1: now_ms
-- 2: burst_window_ms
-- 3: burst_limit
-- 4: sust_window_ms
-- 5: sust_limit
-- 6: idem_key (string or "")
-- 7: idem_ttl_ms

local key_burst = KEYS[1]
local key_sust  = KEYS[2]
local key_ded   = KEYS[3]

local now_ms        = tonumber(ARGV[1])
local burst_win_ms  = tonumber(ARGV[2])
local burst_limit   = tonumber(ARGV[3])
local sust_win_ms   = tonumber(ARGV[4])
local sust_limit    = tonumber(ARGV[5])
local idem_key      = ARGV[6]
local idem_ttl_ms   = tonumber(ARGV[7])

-- Dedupe: if key exists → return remaining/ttl without counting
if key_ded ~= "" and idem_key ~= "" then
  if redis.call('SISMEMBER', key_ded, idem_key) == 1 then
    -- compute current remaining/ttl (without increment)
    redis.call('ZREMRANGEBYSCORE', key_burst, 0, now_ms - burst_win_ms)
    redis.call('ZREMRANGEBYSCORE', key_sust,  0, now_ms - sust_win_ms)

    local burst_cnt = redis.call('ZCARD', key_burst)
    local sust_cnt  = redis.call('ZCARD', key_sust)

    local rem_b = burst_limit - burst_cnt
    local rem_s = sust_limit  - sust_cnt
    local remaining = math.min(rem_b, rem_s)

    -- TTLs
    local ttl_b = redis.call('PTTL', key_burst)
    local ttl_s = redis.call('PTTL', key_sust)
    if ttl_b < 0 then ttl_b = burst_win_ms end
    if ttl_s < 0 then ttl_s = sust_win_ms end
    local ttl = math.max(ttl_b, ttl_s)

    return { remaining, ttl, 1 } -- dedup hit
  end
end

-- Maintain windows
redis.call('ZREMRANGEBYSCORE', key_burst, 0, now_ms - burst_win_ms)
redis.call('ZREMRANGEBYSCORE', key_sust,  0, now_ms - sust_win_ms)

local burst_cnt = redis.call('ZCARD', key_burst)
local sust_cnt  = redis.call('ZCARD', key_sust)

if burst_cnt >= burst_limit or sust_cnt >= sust_limit then
  local ttl_b = redis.call('PTTL', key_burst)
  local ttl_s = redis.call('PTTL', key_sust)
  if ttl_b < 0 then ttl_b = burst_win_ms end
  if ttl_s < 0 then ttl_s = sust_win_ms end
  local ttl = math.max(ttl_b, ttl_s)
  return { -1, ttl, 0 } -- over limit
end

-- Record request in both buckets
local member = tostring(now_ms) .. ":" .. tostring(math.random())
redis.call('ZADD', key_burst, now_ms, member)
redis.call('ZADD', key_sust,  now_ms, member)

-- Ensure expiries
local ttl_b = redis.call('PTTL', key_burst)
local ttl_s = redis.call('PTTL', key_sust)
if ttl_b < 0 or ttl_b > burst_win_ms then redis.call('PEXPIRE', key_burst, burst_win_ms) end
if ttl_s < 0 or ttl_s > sust_win_ms  then redis.call('PEXPIRE', key_sust,  sust_win_ms)  end

-- Add idem key for dedupe after successful "count"
if key_ded ~= "" and idem_key ~= "" then
  redis.call('SADD', key_ded, idem_key)
  redis.call('PEXPIRE', key_ded, idem_ttl_ms)
end

burst_cnt = burst_cnt + 1
sust_cnt  = sust_cnt + 1

local rem_b = burst_limit - burst_cnt
local rem_s = sust_limit  - sust_cnt
local remaining = math.min(rem_b, rem_s)

ttl_b = redis.call('PTTL', key_burst)
ttl_s = redis.call('PTTL', key_sust)
if ttl_b < 0 then ttl_b = burst_win_ms end
if ttl_s < 0 then ttl_s = sust_win_ms end
local ttl = math.max(ttl_b, ttl_s)

return { remaining, ttl, 0 }  -- allowed
"""


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Dual-bucket sliding-window limiter with idempotency-aware dedupe.
    """

    def __init__(
        self,
        app,
        *,
        redis_url: Optional[str] = None,
        # defaults (sane prod starting points)
        burst_limit: int = 10,
        burst_window_s: int = 1,
        sustained_limit: int = 60,
        sustained_window_s: int = 60,
        # path-specific overrides: path -> (burst_limit, burst_window_s, sustained_limit, sustained_window_s)
        per_path_limits: Optional[Dict[str, Tuple[int, int, int, int]]] = None,
        # misc
        jwt_secret: Optional[str] = None,
        allowlist_shops: Optional[Iterable[str]] = None,
        exempt_paths: Optional[Iterable[str]] = None,
        exempt_methods: Optional[Iterable[str]] = None,
        header_prefix: str = "RateLimit",
        idem_methods: Optional[Set[str]] = None,            # which methods apply idempotency dedupe
        idem_header: str = "Idempotency-Key",               # client-provided
        identifier_header: Optional[str] = None,            # e.g., X-User-Id
    ):
        super().__init__(app)
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis: redis.Redis = redis.from_url(self.redis_url, decode_responses=True)

        self.burst_limit = burst_limit
        self.burst_window_s = burst_window_s
        self.sustained_limit = sustained_limit
        self.sustained_window_s = sustained_window_s
        self.per_path_limits = per_path_limits or {}

        self.jwt_secret = jwt_secret or os.getenv("JWT_SECRET", "change_me")
        self.allowlist_shops = set(allowlist_shops or [])
        self.exempt_paths = set(exempt_paths or {"/health", "/metrics", "/docs", "/openapi.json"})
        self.exempt_methods = set(m.upper() for m in (exempt_methods or {"OPTIONS"}))
        self.header_prefix = header_prefix

        self.idem_methods = set(m.upper() for m in (idem_methods or {"POST", "PUT", "PATCH"}))
        self.idem_header = idem_header
        self.identifier_header = (identifier_header or os.getenv("RL_ID_HEADER", "")).lower()

        self._lua_sha: Optional[str] = None

    async def _ensure_lua(self):
        if self._lua_sha:
            return
        try:
            self._lua_sha = await self.redis.script_load(LUA_DUAL_BUCKET)
        except RedisError as e:
            logger.error(f"[RateLimiter] LUA load failed: {e}")
            self._lua_sha = None

    async def dispatch(self, request: Request, call_next):
        # Lightweight, stable timestamp for this request (shared across middlewares)
        if not hasattr(request.state, "now_ms"):
            request.state.now_ms = int(time.time() * 1000)

        path = request.url.path
        method = request.method.upper()

        if path in self.exempt_paths or method in self.exempt_methods:
            return await call_next(request)

        shop = self._extract_shop(request)
        if shop and shop in self.allowlist_shops:
            return await call_next(request)

        identifier = self._identifier(request, shop)
        if not identifier:
            return await call_next(request)

        # limits resolution
        b_lim, b_win, s_lim, s_win = self._limits_for_path(path)
        b_ms = b_win * 1000
        s_ms = s_win * 1000

        # redis keys
        base = f"rl:{path}:{identifier}"
        key_burst = base + ":b"
        key_sust  = base + ":s"

        # idempotency (per identifier+path)
        idem_key = ""
        key_dedupe = ""
        if method in self.idem_methods:
            raw = request.headers.get(self.idem_header)
            if raw:
                # include method to avoid cross-method collisions
                idem_key = f"{method}:{raw}"
                key_dedupe = base + ":idem"

        try:
            await self._ensure_lua()
            args = [
                request.state.now_ms,
                b_ms, b_lim,
                s_ms, s_lim,
                idem_key,
                max(b_ms, s_ms),  # dedupe retention = largest window
            ]

            # run LUA (sha or eval fallback)
            if self._lua_sha:
                try:
                    remaining, ttl_ms, deduped = await self.redis.evalsha(
                        self._lua_sha, 3, key_burst, key_sust, key_dedupe, *args
                    )
                except RedisError:
                    remaining, ttl_ms, deduped = await self.redis.eval(
                        LUA_DUAL_BUCKET, 3, key_burst, key_sust, key_dedupe, *args
                    )
            else:
                remaining, ttl_ms, deduped = await self.redis.eval(
                    LUA_DUAL_BUCKET, 3, key_burst, key_sust, key_dedupe, *args
                )

            remaining = int(remaining)
            ttl_ms = int(ttl_ms)

            # Over limit
            if remaining < 0:
                reset_s = max(1, ttl_ms // 1000)
                headers = self._rate_headers(b_lim, s_lim, 0, reset_s)
                # Add Retry-After with a tiny jitter-friendly floor (1s min)
                headers["Retry-After"] = str(reset_s)
                raise HTTPException(status_code=429, detail="Rate limit exceeded", headers=headers)

            # Allowed → continue
            response: Response = await call_next(request)
            reset_s = max(1, ttl_ms // 1000)
            self._attach_headers(response, b_lim, s_lim, max(0, remaining), reset_s)
            return response

        except HTTPException as he:
            # Attach headers if missing
            if he.status_code == 429 and not he.headers:
                he.headers = self._rate_headers(b_lim, s_lim, 0, s_win)
                he.headers["Retry-After"] = str(s_win)
            raise
        except RedisError as e:
            # bypass on Redis issues
            logger.error(f"[RateLimiter] Redis error, bypassing limiter: {e}")
            return await call_next(request)
        except Exception as e:
            logger.exception(f"[RateLimiter] Unexpected error, bypassing limiter: {e}")
            return await call_next(request)

    # ------------ helpers ------------

    def _extract_shop(self, request: Request) -> Optional[str]:
        q = request.query_params.get("shop")
        if q:
            return q
        cookie = request.cookies.get("session")
        if cookie:
            try:
                payload = jwt.decode(cookie, self.jwt_secret, algorithms=["HS256"])
                s = payload.get("shop")
                if s:
                    return s
            except jwt.ExpiredSignatureError:
                logger.debug("[RateLimiter] JWT expired")
            except jwt.DecodeError:
                logger.debug("[RateLimiter] JWT decode error")
        return None

    def _identifier(self, request: Request, shop: Optional[str]) -> str:
        if shop:
            return f"shop:{shop}"

        if self.identifier_header:
            v = request.headers.get(self.identifier_header)
            if v:
                return f"hdr:{self.identifier_header}:{v}"

        fwd = request.headers.get("x-forwarded-for")
        if fwd:
            ip = fwd.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        return f"ip:{ip}"

    def _limits_for_path(self, path: str) -> Tuple[int, int, int, int]:
        # exact match first
        if path in self.per_path_limits:
            return self.per_path_limits[path]
        return self.burst_limit, self.burst_window_s, self.sustained_limit, self.sustained_window_s

    def _rate_headers(self, b_limit: int, s_limit: int, remaining: int, reset_s: int):
        # Conservative: expose the stricter policy via standard-ish headers
        prefix = self.header_prefix
        # Many clients just need one set; we expose sustained as "limit"
        return {
            f"{prefix}-Limit": str(s_limit),
            f"{prefix}-Remaining": str(max(0, remaining)),
            f"{prefix}-Reset": str(max(1, reset_s)),
        }

    def _attach_headers(self, response: Response, b_limit: int, s_limit: int, remaining: int, reset_s: int):
        for k, v in self._rate_headers(b_limit, s_limit, remaining, reset_s).items():
            response.headers[k] = v
