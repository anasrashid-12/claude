// frontend/src/app/dashboard/upload/page.tsx
'use client'

import { useState } from "react"

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [shop, setShop] = useState('ai-image-app-dev-store.myshopify.com') // Replace with dynamic value in production
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setMessage('')

    try {
      // Step 1: Upload the file to backend
      const formData = new FormData()
      formData.append('image', file)

      const uploadRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`, {
        method: 'POST',
        body: formData,
      })

      const uploadData = await uploadRes.json()
      const imageUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/uploads/${uploadData.filename}`

      // Step 2: Call image/process to queue the job
      const processRes = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_url: imageUrl, shop }),
      })

      const result = await processRes.json()

      if (result.success) {
        setMessage('✅ Image queued for processing!')
      } else {
        setMessage('❌ Failed to process image.')
      }
    } catch (error) {
      console.error(error)
      setMessage('❌ Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Upload Image</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="mb-4"
      />

      <button
        onClick={handleUpload}
        disabled={loading || !file}
        className="px-4 py-2 bg-black text-white rounded-xl hover:bg-gray-800 disabled:opacity-50"
      >
        {loading ? 'Uploading...' : 'Upload & Queue'}
      </button>

      {message && <p className="mt-4 text-sm">{message}</p>}
    </div>
  )
}
