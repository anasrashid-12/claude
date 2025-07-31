// utils/supabase/client.ts
'use client';

import { createBrowserClient } from '@supabase/ssr';
import { SupabaseClient } from '@supabase/supabase-js';
import { getCookie } from 'cookies-next';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Singleton instance
let supabase: SupabaseClient | null = null;

export const getSupabase = (): SupabaseClient => {
  const token = getCookie('session') as string;

  if (!supabase) {
    supabase = createBrowserClient(supabaseUrl, supabaseAnonKey, {
      global: {
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      }
    });
  }

  return supabase;
};
