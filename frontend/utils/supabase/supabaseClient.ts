'use client';

import { createBrowserClient } from '@supabase/ssr';
import { SupabaseClient } from '@supabase/supabase-js';
import { getCookie } from 'cookies-next';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const getSupabase = (): SupabaseClient => {
  return createBrowserClient(supabaseUrl, supabaseAnonKey, {
    global: {
      fetch: async (url, options: RequestInit = {}) => {
        const token = getCookie('session');

        const headers: HeadersInit = {
          'Content-Type': 'application/json',
          apikey: supabaseAnonKey, // ✅ always include apikey
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(options.headers || {}),
        };

        // Optional: log for debugging (remove in production)
        console.log('Supabase fetch with headers:', headers);

        return fetch(url, {
          ...options,
          headers,
        });
      },
    },
  });
};
