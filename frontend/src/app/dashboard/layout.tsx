// frontend/app/(dashboard)/dashboard/layout.tsx
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    return (
      <div className="min-h-screen p-6">
        {children}
      </div>
    );
  }
  