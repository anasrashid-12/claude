import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
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
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];

    if (files.length === 0) {
      return NextResponse.json(
        { error: 'No files provided' },
        { status: 400 }
      );
    }

    // Send files to backend processing service
    const processingRequests = files.map(async (file) => {
      const fileData = new FormData();
      fileData.append('file', file);
      fileData.append('session_token', session.value);

      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        body: fileData,
      });

      if (!response.ok) {
        throw new Error(`Failed to process ${file.name}`);
      }

      return response.json();
    });

    const results = await Promise.all(processingRequests);

    return NextResponse.json({
      message: 'Processing started',
      results: results.map((result, index) => ({
        id: result.id,
        originalName: files[index].name,
        url: result.original_url,
        processedUrl: null, // Will be updated when processing completes
        status: 'processing',
        createdAt: new Date().toISOString()
      }))
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Failed to process images' },
      { status: 500 }
    );
  }
} 