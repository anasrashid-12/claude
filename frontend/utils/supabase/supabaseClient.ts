'use client';

import { createBrowserClient } from '@supabase/ssr';
import { SupabaseClient } from '@supabase/supabase-js';
import { getCookie } from 'cookies-next';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const getSupabase = (): SupabaseClient => {
  const token = getCookie('session');

  return createBrowserClient(supabaseUrl, supabaseAnonKey, {
    global: {
      fetch: (url, options = {}) => {
        const headers = {
          'Content-Type': 'application/json', // ✅ fixed here
          apikey: supabaseAnonKey,
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...options.headers,
        };

        return fetch(url, {
          ...options,
          headers,
        });
      },
    },
  });
};
