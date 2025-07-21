'use client';

import UploadSection from '@/components/UploadSection';

export default function UploadClient() {
  return (
    <div className="px-4 sm:px-6 pt-10 pb-16 max-w-2xl mx-auto text-gray-900 dark:text-white">
      <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">📤 Upload Images</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Upload single or batch images to process them with AI.
      </p>

      <div className="rounded-xl bg-white dark:bg-[#1e293b] p-6 shadow-lg">
        <UploadSection />
      </div>
    </div>
  );
}
