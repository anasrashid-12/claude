'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '../../../lib/utils';

const navItems = [
  { href: '/dashboard/upload', label: '📤 Upload' },
  { href: '/dashboard/queue', label: '📋 Queue' },
  { href: '/dashboard/gallery', label: '🖼️ Gallery' },
  { href: '/dashboard/settings', label: '⚙️ Settings' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-full sm:w-64 bg-white border-r border-gray-200 p-6 min-h-screen">
      {/* App Logo / Name */}
      <div className="mb-10">
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
          🧠 Maxflow AI
        </h1>
        <p className="text-xs text-gray-500">Smart Image Tools for Shopify</p>
      </div>

      {/* Navigation Links */}
      <nav className="space-y-2">
        {navItems.map(({ href, label }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                'block px-4 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150',
                isActive
                  ? 'bg-black text-white shadow'
                  : 'text-gray-700 hover:bg-gray-100'
              )}
            >
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
