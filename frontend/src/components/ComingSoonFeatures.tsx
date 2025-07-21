'use client';

const features = [
  { name: 'Keyword Research', eta: 'Coming Q3 2025' },
  { name: 'Analytics Dashboard', eta: 'Coming Q2 2025' },
  { name: 'WooCommerce Integration', eta: 'Coming Q4 2025' },
];

export default function ComingSoonFeatures() {
  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow p-5 w-full">
      <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-4">
        🚀 Features Coming Soon
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {features.map(({ name, eta }, idx) => (
          <div
            key={idx}
            className="rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-4 text-xs sm:text-sm transition hover:shadow-md"
          >
            <div className="font-medium text-gray-900 dark:text-white">{name}</div>
            <div className="text-gray-500 dark:text-gray-400">{eta}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
