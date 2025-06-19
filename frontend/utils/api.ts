const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

export const getImagesByShop = async (shop: string) => {
  if (!shop) {
    console.warn('No shop provided to getImagesByShop.');
    return null;
  }

  try {
    const res = await fetch(`${BASE_URL}/image/supabase/get-images?shop=${encodeURIComponent(shop)}`, {
      credentials: 'include',
    });

    if (!res.ok) {
      console.error(`Failed to fetch images. Status: ${res.status}`);
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error('Error fetching images:', error);
    return null;
  }
};

export const queueImage = async (image_url: string, shop: string) => {
  if (!image_url || !shop) {
    console.warn('Missing image_url or shop in queueImage.');
    return null;
  }

  try {
    const res = await fetch(`${BASE_URL}/image/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ image_url, shop }),
    });

    if (!res.ok) {
      const errMsg = await res.text();
      console.error(`Image queue failed. Status: ${res.status}. Message: ${errMsg}`);
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error('Error queueing image:', error);
    return null;
  }
};
