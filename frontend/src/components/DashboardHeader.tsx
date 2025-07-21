'use client';

type DashboardHeaderProps = {
  title: string;
  subtitle?: string;
};

export default function DashboardHeader({ title, subtitle }: DashboardHeaderProps) {
  return (
    <header className="mb-6">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{title}</h1>
      {subtitle && (
        <p className="mt-2 text-base text-gray-600 dark:text-gray-400">{subtitle}</p>
      )}
    </header>
  );
}
