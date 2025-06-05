'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';

interface Stats {
  totalUploads: number;
  processingCount: number;
  completedCount: number;
  failedCount: number;
}

interface RecentUpload {
  id: string;
  filename: string;
  status: 'processing' | 'completed' | 'failed';
  imageUrl?: string;
  createdAt: string;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats>({
    totalUploads: 0,
    processingCount: 0,
    completedCount: 0,
    failedCount: 0
  });

  const [recentUploads, setRecentUploads] = useState<RecentUpload[]>([]);

  // TODO: Replace with actual API call
  useEffect(() => {
    // Simulated data for now
    setStats({
      totalUploads: 15,
      processingCount: 2,
      completedCount: 12,
      failedCount: 1
    });

    setRecentUploads([
      {
        id: '1',
        filename: 'product1.jpg',
        status: 'completed',
        imageUrl: 'https://via.placeholder.com/150',
        createdAt: new Date().toISOString()
      },
      // Add more mock data as needed
    ]);
  }, []);

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Total Uploads</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.totalUploads}</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Processing</dt>
            <dd className="mt-1 text-3xl font-semibold text-yellow-500">{stats.processingCount}</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Completed</dt>
            <dd className="mt-1 text-3xl font-semibold text-green-500">{stats.completedCount}</dd>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Failed</dt>
            <dd className="mt-1 text-3xl font-semibold text-red-500">{stats.failedCount}</dd>
          </div>
        </div>
      </div>

      {/* Recent Uploads */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Uploads</h3>
          <Link 
            href="/dashboard/upload"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            Upload New
          </Link>
        </div>
        <div className="border-t border-gray-200">
          <ul role="list" className="divide-y divide-gray-200">
            {recentUploads.map((upload) => (
              <li key={upload.id} className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {upload.imageUrl && (
                      <div className="flex-shrink-0 h-12 w-12 relative">
                        <Image
                          src={upload.imageUrl}
                          alt={upload.filename}
                          fill
                          className="rounded-md object-cover"
                        />
                      </div>
                    )}
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-900">{upload.filename}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(upload.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <div>
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
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
} 