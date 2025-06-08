import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

interface ImageProcessorProps {
  onProcess: (file: File) => Promise<void>
  processingType: 'background-removal' | 'enhancement' | 'batch'
}

export default function ImageProcessor({ onProcess, processingType }: ImageProcessorProps) {
  const [isProcessing, setIsProcessing] = useState(false)
  const [preview, setPreview] = useState<string | null>(null)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    setPreview(URL.createObjectURL(file))

    try {
      setIsProcessing(true)
      await onProcess(file)
    } catch (error) {
      console.error('Error processing image:', error)
    } finally {
      setIsProcessing(false)
    }
  }, [onProcess])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    multiple: processingType === 'batch'
  })

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}`}
      >
        <input {...getInputProps()} />
        {preview ? (
          <div className="relative">
            <img
              src={preview}
              alt="Preview"
              className="max-h-64 mx-auto rounded-lg"
            />
            {isProcessing && (
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <p className="text-lg text-gray-600">
              {isDragActive
                ? 'Drop your images here...'
                : 'Drag & drop images here, or click to select'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Supported formats: JPEG, PNG, WebP
            </p>
          </div>
        )}
      </div>
    </div>
  )
} 