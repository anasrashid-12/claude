// app/api/dashboard-stats/route.ts
import { supabaseServer } from '../../../../utils/supabase/server';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { shop } = await req.json();

  const { data: images, error } = await supabaseServer
    .from('images')
    .select('*')
    .eq('shop', shop)
    .order('created_at', { ascending: false });

  if (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }

  const stats = {
    total: images.length,
    processing: images.filter(img => ['processing', 'queued'].includes(img.status)).length,
    failed: images.filter(img => ['failed', 'error'].includes(img.status)).length,
    completed: images.filter(img => ['processed', 'completed'].includes(img.status)).length,
  };

  const recent = images
    .filter(img => img.processed_url)
    .slice(0, 5)
    .map(img => ({
      url: img.processed_url!,
      product: img.image_url?.split('/').pop() ?? 'Unnamed',
      status:
        ['processed', 'completed'].includes(img.status)
          ? 'Complete'
          : ['processing', 'queued'].includes(img.status)
          ? 'Importing'
          : ['failed', 'error'].includes(img.status)
          ? 'Failed'
          : 'Unknown',
    }));

  return NextResponse.json({ stats, recent });
}
