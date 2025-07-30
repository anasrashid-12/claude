// utils/supabase/server.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY!; 

console.log('SERVICE ROLE KEY:', process.env.SUPABASE_SERVICE_ROLE_KEY);

export const supabaseServer = createClient(supabaseUrl, serviceRoleKey, {
  global: {
    headers: {
      Authorization: `Bearer ${serviceRoleKey}`
    }
  }
});
