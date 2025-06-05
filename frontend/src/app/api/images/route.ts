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
    const url = new URL(request.url);
    const page = url.searchParams.get('page') || '1';
    const limit = url.searchParams.get('limit') || '20';

    // Fetch images from backend service
    const response = await fetch(`http://localhost:8000/api/images?page=${page}&limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${session.value}`
      }
    });

    if (!response.ok) {
      throw new Error('Failed to fetch images');
    }

    const data = await response.json();
    return NextResponse.json({
      success: true,
      data: {
        items: data.items,
        hasNextPage: data.has_next_page,
        totalItems: data.total_items
      }
    });

  } catch (error) {
    console.error('Images fetch error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to fetch images',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 