'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';

interface UploadRecord {
  id: string;
  filename: string;
  status: 'processing' | 'completed' | 'failed';
  imageUrl: string;
  createdAt: string;
  fileSize: number;
}

export default function HistoryPage() {
  const [uploads, setUploads] = useState<UploadRecord[]>([]);
  const [filter, setFilter] = useState<'all' | 'completed' | 'processing' | 'failed'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'size'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    // TODO: Replace with actual API call
    const mockData: UploadRecord[] = [
      {
        id: '1',
        filename: 'product1.jpg',
        status: 'completed',
        imageUrl: 'https://via.placeholder.com/150',
        createdAt: new Date().toISOString(),
        fileSize: 1024 * 1024 * 2 // 2MB
      },
      // Add more mock data as needed
    ];

    setUploads(mockData);
  }, []);

  const filteredAndSortedUploads = uploads
    .filter((upload) => filter === 'all' || upload.status === filter)
    .sort((a, b) => {
      if (sortBy === 'date') {
        return sortOrder === 'asc'
          ? new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
          : new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      }
      if (sortBy === 'name') {
        return sortOrder === 'asc'
          ? a.filename.localeCompare(b.filename)
          : b.filename.localeCompare(a.filename);
      }
      // size
      return sortOrder === 'asc'
        ? a.fileSize - b.fileSize
        : b.fileSize - a.fileSize;
    });

  return (
    <div className="space-y-6">
      {/* Filters and Sort Controls */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label htmlFor="filter" className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              id="filter"
              value={filter}
              onChange={(e) => setFilter(e.target.value as typeof filter)}
              className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
            >
              <option value="all">All</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <div>
            <label htmlFor="sort" className="block text-sm font-medium text-gray-700">
              Sort by
            </label>
            <select
              id="sort"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
            >
              <option value="date">Date</option>
              <option value="name">Name</option>
              <option value="size">Size</option>
            </select>
          </div>

          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Upload List */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Image
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Name
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Size
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                Date
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAndSortedUploads.map((upload) => (
              <tr key={upload.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex-shrink-0 h-10 w-10 relative">
                    <Image
                      src={upload.imageUrl}
                      alt={upload.filename}
                      fill
                      className="rounded-lg object-cover"
                    />
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {upload.filename}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      upload.status === 'completed'
                        ? 'bg-green-100 text-green-800'
                        : upload.status === 'processing'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {upload.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {(upload.fileSize / 1024 / 1024).toFixed(2)} MB
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(upload.createdAt).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 