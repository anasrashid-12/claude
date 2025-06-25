const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

if (!BASE_URL) {
  throw new Error('❌ Missing NEXT_PUBLIC_BACKEND_URL in environment');
}

/**
 * ✅ Fetch images for the authenticated shop
 */
export const getImagesByShop = async () => {
  try {
    const res = await fetch(`${BASE_URL}/image/supabase/get-images`, {
      credentials: 'include',
    });

    if (!res.ok) {
      console.error(`[getImagesByShop] ❌ Failed: ${res.status}`);
      return [];
    }

    const data = await res.json();
    return data?.images || [];
  } catch (error) {
    console.error('[getImagesByShop] ❌ Error:', error);
    return [];
  }
};

/**
 * ✅ Queue image for processing
 */
export const queueImage = async (image_url: string) => {
  if (!image_url) {
    console.warn('[queueImage] No image URL provided');
    return null;
  }

  try {
    const res = await fetch(`${BASE_URL}/image/process`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url }),
    });

    if (!res.ok) {
      const errorMsg = await res.text();
      console.error(`[queueImage] ❌ Failed: ${res.status} - ${errorMsg}`);
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error('[queueImage] ❌ Error:', error);
    return null;
  }
};
