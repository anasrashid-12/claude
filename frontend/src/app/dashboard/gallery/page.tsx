// frontend/src/app/dashboard/gallery/page.tsx
'use client'

import { useEffect, useState } from 'react'

interface ImageItem {
  id: string
  status: string
  image_url: string
  processed_url?: string
  error_message?: string
}

export default function GalleryPage() {
  const [images, setImages] = useState<ImageItem[]>([])
  const [loading, setLoading] = useState(true)

  const shop = 'ai-image-app-dev-store.myshopify.com' // Replace dynamically later

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_BACKEND_URL}/supabase/get-images?shop=${shop}`
        )
        const data = await res.json()
        setImages(data.images || [])
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchImages()
  }, [])

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">📸 Processed Gallery</h1>

      {loading ? (
        <p>Loading...</p>
      ) : images.length === 0 ? (
        <p>No images found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {images.map((img) => (
            <div key={img.id} className="border rounded-xl p-2 shadow">
              <img
                src={img.processed_url || img.image_url}
                alt="Processed"
                className="w-full h-48 object-cover rounded"
              />
              <div className="mt-2 text-sm">
                Status:{' '}
                {img.status === 'processed' ? (
                  <span className="text-green-600">✅ Done</span>
                ) : img.status === 'queued' ? (
                  <span className="text-yellow-600">🕒 Queued</span>
                ) : (
                  <span className="text-red-600">❌ Error</span>
                )}
              </div>
              {img.error_message && (
                <p className="text-xs text-red-500 mt-1">{img.error_message}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
