import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
  // Verify authentication
  const cookieStore = cookies();
  const session = cookieStore.get('shopify_session');
  
  if (!session) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }

  try {
    // Fetch processing stats from backend
    const response = await fetch('http://localhost:8000/api/stats', {
      headers: {
        'Authorization': `Bearer ${session.value}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch processing stats');
    }

    const data = await response.json();
    return NextResponse.json({
      totalProcessed: data.total_processed,
      inQueue: data.in_queue,
      failedJobs: data.failed_jobs,
      averageProcessingTime: data.average_processing_time
    });

  } catch (error) {
    console.error('Stats error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch processing stats' },
      { status: 500 }
    );
  }
} 