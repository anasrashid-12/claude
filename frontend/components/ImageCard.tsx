/// FILE: components/ImageCard.tsx
export default function ImageCard({ task }: { task: any }) {
    return (
      <div className='border rounded p-2'>
        <img src={task.processed_url ?? task.original_url} className='w-full h-48 object-contain' />
        <div className='mt-2 text-center'>
          <span className='px-2 py-1 bg-gray-200 rounded'>{task.status}</span>
        </div>
      </div>
    )
  }