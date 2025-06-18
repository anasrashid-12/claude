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
      <aside className="w-64 p-6 bg-white border-r">
        <h2 className="text-xl font-semibold mb-6">Maxflow App</h2>
        <nav className="space-y-2">
          {navItems.map(({ href, label }) => (
            <Link key={href} href={href}>
              <span
                className={`block px-4 py-2 rounded-lg text-sm font-medium ${
                  pathname === href
                    ? 'bg-black text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                {label}
              </span>
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}
