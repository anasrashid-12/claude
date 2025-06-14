/// FILE: components/QueueStatus.tsx
'use client'
import { useEffect, useState } from 'react'

export default function QueueStatus() {
  const [tasks, setTasks] = useState<any[]>([])
  const token = sessionStorage.getItem('jwt') || ''

  const fetchQueue = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/tasks/status`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (res.ok) setTasks(await res.json())
  }

  useEffect(() => {
    fetchQueue()
    const id = setInterval(fetchQueue, 5000)
    return () => clearInterval(id)
  }, [])

  return (
    <div className='p-4'>
      <h2 className='text-lg'>Processing Queue</h2>
      {tasks.map(t => (
        <div key={t.id} className='text-sm'>
          {t.original_url.split('/').pop()} — {t.status}
        </div>
      ))}
    </div>
  )
}
