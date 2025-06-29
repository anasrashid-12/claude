const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL!;
if (!BASE_URL) {
  throw new Error('❌ NEXT_PUBLIC_BACKEND_URL missing in .env.local');
}

/**
 * Fetch images from backend filtered by shop
 */
export const getImagesByShop = async (shop: string) => {
  try {
    const res = await fetch(`${BASE_URL}/image/supabase/get-images`, {
      credentials: 'include',
    });

    if (!res.ok) {
      console.error('❌ Failed to fetch images');
      return [];
    }

    const { images = [] } = await res.json();
    return images.filter((img: any) => img.shop === shop);
  } catch (error) {
    console.error('❌ Error fetching images:', error);
    return [];
  }
};

/**
 * Queue image for processing
 */
export const queueImage = async (imageUrl: string) => {
  try {
    const res = await fetch(`${BASE_URL}/image/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ image_url: imageUrl }),
    });

    if (!res.ok) {
      console.error('❌ Failed to queue image');
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error('❌ Error queuing image:', error);
    return null;
  }
};
