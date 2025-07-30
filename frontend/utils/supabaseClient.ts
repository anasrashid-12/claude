'use client';

import { createBrowserClient } from '@supabase/ssr';
import { SupabaseClient } from '@supabase/supabase-js';
import { getCookie } from 'cookies-next'; // ✅ This import was missing

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Singleton instance shared across components
let supabase: SupabaseClient | null = null;

export const getSupabase = (): SupabaseClient => {
  if (!supabase) {
    supabase = createBrowserClient(supabaseUrl, supabaseAnonKey, {
      global: {
        headers: {
          // read shop session from cookie and pass it manually
          Authorization: `Bearer ${getCookie('session')}`,
        },
      },
    });
  }
  return supabase;
};
