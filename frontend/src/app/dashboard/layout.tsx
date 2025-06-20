'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard/upload', label: 'Upload' },
  { href: '/dashboard/gallery', label: 'Gallery' },
  { href: '/dashboard/settings', label: 'Settings' },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r p-6">
        <h1 className="text-xl font-bold mb-8">Maxflow App</h1>
        <nav aria-label="Sidebar navigation" className="space-y-2">
          {navItems.map(({ href, label }) => {
            const isActive = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                title={`Go to ${label}`}
                aria-current={isActive ? 'page' : undefined}
                className={`block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-black text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 sm:p-8 overflow-y-auto bg-gray-50">
        {children}
      </main>
    </div>
  );
}
