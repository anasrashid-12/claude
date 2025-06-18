export const getImagesByShop = async (shop: string) => {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`);
    return res.ok ? await res.json() : null;
  } catch (error) {
    console.error("Error fetching images:", error);
    return null;
  }
};

export const queueImage = async (image_url: string, shop: string) => {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_url, shop }),
    });
    return res.ok ? await res.json() : null;
  } catch (error) {
    console.error("Error queueing image:", error);
    return null;
  }
};