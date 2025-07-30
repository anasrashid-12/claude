'use client';

type ImportItem = {
  url: string;
  product: string;
  status: string;
};

export default function RecentImportsTable({ items }: { items: ImportItem[] }) {
  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow p-5 w-full overflow-x-auto">
      <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-4">
        📦 Recent Imports
      </h2>

      {items.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400 text-sm">📭 No recent imports yet.</p>
      ) : (
        <table className="w-full text-xs sm:text-sm table-auto">
          <thead className="text-left text-gray-500 dark:text-gray-400">
            <tr>
              <th className="py-2 pr-4">URL</th>
              <th className="py-2 pr-4">Product</th>
              <th className="py-2">Status</th>
            </tr>
          </thead>
          <tbody className="text-gray-900 dark:text-gray-200">
            {items.map((item, idx) => (
              <tr key={idx} className="border-t border-gray-100 dark:border-gray-800">
                <td className="py-2 pr-4 truncate max-w-xs text-blue-600 dark:text-blue-400 underline">
                  <a href={item.url} target="_blank" rel="noopener noreferrer">
                    {item.url}
                  </a>
                </td>
                <td className="py-2 pr-4">{item.product}</td>
                <td className="py-2">
                  {item.status === 'Complete' ? (
                    <span className="text-green-600 dark:text-green-400">✅ Complete</span>
                  ) : item.status === 'Importing' ? (
                    <span className="text-blue-600 dark:text-blue-400">⏳ Importing</span>
                  ) : item.status === 'Failed' ? (
                    <span className="text-red-500 dark:text-red-400">❌ Failed</span>
                  ) : (
                    <span className="text-gray-600 dark:text-gray-300">🔄 {item.status}</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
