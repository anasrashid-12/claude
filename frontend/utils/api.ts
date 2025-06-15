// frontend/utils/api.ts
export const getImagesByShop = async (shop: string) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/supabase/get-images?shop=${shop}`);
    return res.ok ? await res.json() : null;
  };
  
  export const queueImage = async (image_url: string, shop: string) => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/image/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_url, shop }),
    });
    return res.ok ? await res.json() : null;
  };
  