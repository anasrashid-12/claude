// frontend/components/UploadForm.tsx
"use client";

import { useState } from "react";
import { queueImage } from "../utils/api";

export default function UploadForm({ shop, onUpload }: { shop: string; onUpload: () => void }) {
  const [imageUrl, setImageUrl] = useState("");

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    if (!imageUrl) return;
    const res = await queueImage(imageUrl, shop);
    if (res?.success) {
      setImageUrl("");
      onUpload();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <input
        type="url"
        value={imageUrl}
        onChange={(e) => setImageUrl(e.target.value)}
        placeholder="Enter image URL"
        className="border p-3 rounded w-full"
      />
      <button type="submit" className="bg-black text-white py-2 px-4 rounded hover:bg-gray-800">
        Upload and Queue
      </button>
    </form>
  );
}
