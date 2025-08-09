'use client';

import { Bell, CircleHelp, Moon, Sun, Menu } from 'lucide-react';
import { useTheme } from './ThemeProvider';
import useShop from '@/hooks/useShop';
import useAvatar from '@/hooks/useAvatar';
import Image from 'next/image';

export default function TopBar({ onMenuClick }: { onMenuClick: () => void }) {
  const { theme, toggleTheme } = useTheme();
  const { shop, loading: shopLoading, error } = useShop();
  const { avatarUrl, loading: avatarLoading } = useAvatar();

  return (
    <div className="sticky top-0 z-50 flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
      <button onClick={onMenuClick} className="md:hidden text-gray-700 dark:text-white z-50">
        <Menu className="w-6 h-6" />
      </button>

      <div className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white truncate max-w-[60%]">
        {/* You can add title or leave empty */}
      </div>

      <div className="flex items-center gap-4">
        {/* Credits display */}
        <div className="text-sm font-medium text-gray-700 dark:text-gray-300 min-w-[90px] text-right">
          {shopLoading ? (
            <span>Loading credits...</span>
          ) : error ? (
            <span className="text-red-500">Error</span>
          ) : (
            <>
              Credits: <span className="font-bold">{shop?.credits ?? 0}</span>
            </>
          )}
        </div>

        <button
          onClick={toggleTheme}
          className="text-gray-500 dark:text-gray-300 hover:text-black dark:hover:text-white transition"
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        <button className="text-gray-500 dark:text-gray-300 hover:text-black dark:hover:text-white transition" aria-label="Help">
          <CircleHelp className="w-5 h-5" />
        </button>

        <button className="text-gray-500 dark:text-gray-300 hover:text-black dark:hover:text-white transition" aria-label="Notifications">
          <Bell className="w-5 h-5" />
        </button>

        <div className="w-8 h-8 rounded-full border border-gray-300 dark:border-gray-700 overflow-hidden">
          {avatarLoading ? (
            <div className="w-full h-full animate-pulse bg-gray-200 dark:bg-gray-700 rounded-full" />
          ) : (
            <Image
              src={avatarUrl || 'https://avatars.githubusercontent.com/u/1?v=4'}
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
