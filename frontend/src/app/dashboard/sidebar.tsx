'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard/upload', label: 'Upload' },
  { href: '/dashboard/queue', label: 'Queue' },
  { href: '/dashboard/gallery', label: 'Gallery' },
  { href: '/dashboard/settings', label: 'Settings' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r p-6">
      <h1 className="text-xl font-bold mb-8">Maxflow App</h1>
      <nav className="space-y-2">
        {navItems.map(({ href, label }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`block px-4 py-2 rounded-lg text-sm font-medium ${
                isActive ? 'bg-black text-white' : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
