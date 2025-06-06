from typing import Optional
import shopify
from app.models.store import Store, StoreCreate, StoreUpdate
from app.repositories.store import StoreRepository
from app.services.base import BaseService
from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError

class StoreService(BaseService[Store, StoreCreate, StoreUpdate, StoreRepository]):
    def __init__(self):
        super().__init__(StoreRepository)

    async def get_by_domain(self, shop_domain: str) -> Optional[Store]:
        """Get a store by its domain"""
        return await self.repository.get_by_domain(shop_domain)

    async def get_active_by_domain(self, shop_domain: str) -> Store:
        """Get an active store by its domain or raise error"""
        store = await self.repository.get_active_by_domain(shop_domain)
        if not store:
            raise AuthenticationError(f"Store {shop_domain} not found or inactive")
        return store

    async def install_store(self, shop_domain: str, access_token: str) -> Store:
        """Install or update a Shopify store"""
        try:
            # Initialize Shopify session
            session = shopify.Session(shop_domain, settings.API_VERSION, access_token)
            shopify.ShopifyResource.activate_session(session)

            # Get shop information
            shop = shopify.Shop.current()
            
            # Create or update store
            store_data = {
                "shop_domain": shop_domain,
                "access_token": access_token,
                "is_active": True,
                "shop_name": shop.name,
                "shop_email": shop.email,
                "shop_owner": shop.shop_owner,
                "shop_plan": shop.plan_name,
                "shop_country": shop.country_code,
                "shop_currency": shop.currency,
                "shop_timezone": shop.timezone,
                "myshopify_domain": shop.myshopify_domain,
                "primary_locale": shop.primary_locale,
                "plan_name": shop.plan_name,
                "plan_display_name": shop.plan_display_name,
            }

            existing_store = await self.get_by_domain(shop_domain)
            if existing_store:
                updated_store = await self.repository.update(
                    existing_store.id,
                    StoreUpdate(**store_data)
                )
            else:
                updated_store = await self.repository.create(
                    StoreCreate(**store_data)
                )

            return updated_store

        except shopify.ValidationException as e:
            raise ValidationError(f"Invalid Shopify credentials: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Failed to install store: {str(e)}")
        finally:
            shopify.ShopifyResource.clear_session()

    async def uninstall_store(self, shop_domain: str) -> bool:
        """Uninstall a Shopify store"""
        store = await self.get_by_domain(shop_domain)
        if not store:
            return False

        try:
            # Update store status
            await self.repository.update(
                store.id,
                StoreUpdate(
                    is_active=False,
                    access_token=None
                )
            )
            return True
        except Exception as e:
            raise ValidationError(f"Failed to uninstall store: {str(e)}")

    def validate_hmac(self, shop_domain: str, hmac: str, params: dict) -> bool:
        """Validate Shopify HMAC signature"""
        try:
            return shopify.Session.validate_params(params)
        except Exception:
            return False

    def build_auth_url(self, shop_domain: str, redirect_uri: str) -> str:
        """Build Shopify OAuth URL"""
        try:
            session = shopify.Session(shop_domain, settings.API_VERSION)
            return session.create_permission_url(
                settings.SHOPIFY_SCOPES,
                redirect_uri
            )
        except Exception as e:
            raise ValidationError(f"Failed to build auth URL: {str(e)}")

    async def exchange_code_for_token(self, shop_domain: str, code: str) -> str:
        """Exchange authorization code for access token"""
        try:
            session = shopify.Session(shop_domain, settings.API_VERSION)
            access_token = session.request_token(code)
            return access_token
        except Exception as e:
            raise AuthenticationError(f"Failed to exchange code for token: {str(e)}")

store_service = StoreService() 