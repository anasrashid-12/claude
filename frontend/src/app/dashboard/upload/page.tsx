// upload/page.tsx
import { Suspense } from 'react';
import UploadClient from './upload-client';

export default function UploadPage() {
  return (
    <Suspense fallback={<div>Loading Upload...</div>}>
      <UploadClient />
    </Suspense>
  );
}
