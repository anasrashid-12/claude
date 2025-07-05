'use client';

import UploadSection from '@/components/UploadSection';
import ClientLayout from '@/components/ClientLayout';

export default function UploadClient() {
  return (
    <ClientLayout>
      <div className="max-w-4xl mx-auto px-6 py-4">
        <header className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800">📤 Upload Images</h1>
          <p className="text-sm text-gray-600">
            Upload single or batch images to process them with AI.
          </p>
        </header>
        <UploadSection />
      </div>
    </ClientLayout>
  );
}
