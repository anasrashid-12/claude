'use client';

import { Bell, CircleHelp, Moon, Sun } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import useShop from '@/hooks/useShop';
import { useEffect, useState } from 'react';
import Image from 'next/image';
import { getSupabase } from '../../utils/supabaseClient'; // Adjust path if needed

export default function TopBar() {
  const { theme, toggleTheme } = useTheme();
  const { shop } = useShop();
  const [avatar, setAvatar] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const supabase = getSupabase();

  useEffect(() => {
    if (!shop) return;

    const fetchAvatar = async () => {
      setLoading(true);
      const { data } = await supabase
        .from('settings')
        .select('avatar_url')
        .eq('shop', shop)
        .single();

      if (data?.avatar_url) setAvatar(data.avatar_url);
      setLoading(false);
    };

    fetchAvatar();

    const channel = supabase
      .channel(`realtime:settings-${shop}`)
      .on(
        'postgres_changes' as any,
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'settings',
          filter: `shop=eq.${shop}`,
        },
        (payload: any) => {
          const updated = payload.new as { avatar_url?: string };
          if (updated?.avatar_url) setAvatar(updated.avatar_url);
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [shop]);

  return (
    <div className="flex flex-wrap justify-between items-center px-4 sm:px-6 py-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      <div className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white truncate max-w-[60%]">
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="text-gray-500 dark:text-gray-300 hover:text-black dark:hover:text-white transition"
          title="Toggle Theme"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        <button
          className="text-gray-500 dark:text-gray-300 hover:text-black dark:hover:text-white transition"
          title="Help"
        >
          <CircleHelp className="w-5 h-5" />
        </button>

        <button
          className="text-gray-500 dark:text-gray-300 hover:text-black dark:hover:text-white transition"
          title="Notifications"
        >
          <Bell className="w-5 h-5" />
        </button>

        <div className="w-8 h-8 rounded-full border border-gray-300 dark:border-gray-700 overflow-hidden">
          {loading ? (
            <div className="w-full h-full animate-pulse bg-gray-200 dark:bg-gray-700 rounded-full" />
          ) : (
            <Image
              src={avatar || 'https://avatars.githubusercontent.com/u/1?v=4'}
              alt="User Avatar"
              width={32}
              height={32}
              unoptimized
              className="rounded-full object-cover"
            />
          )}
        </div>
      </div>
    </div>
  );
}
