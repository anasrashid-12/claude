'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '../../lib/utils';
import { PackageOpen, ImageIcon, Settings, Upload, LayoutDashboard } from 'lucide-react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/dashboard/upload', label: 'Upload', icon: Upload },
  { href: '/dashboard/queue', label: 'Queue', icon: PackageOpen },
  { href: '/dashboard/gallery', label: 'Gallery', icon: ImageIcon },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden sm:block w-64 min-h-screen bg-white dark:bg-[#1e293b] border-r border-gray-200 dark:border-gray-700 p-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        🧠 Maxflow AI
      </h1>
      <nav className="space-y-2">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'flex items-center gap-3 px-4 py-2 rounded-lg text-sm font-medium transition-all',
                isActive
                  ? 'bg-black text-white shadow'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:pl-5'
              )}
            >
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
