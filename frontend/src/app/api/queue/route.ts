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
    // Fetch queue status from backend
    const response = await fetch('http://localhost:8000/api/queue', {
      headers: {
        'Authorization': `Bearer ${session.value}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch queue status');
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Queue status error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch queue status' },
      { status: 500 }
    );
  }
} 