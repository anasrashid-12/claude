export async function checkAuth(shop?: string): Promise<boolean> {
    try {
      const res = await fetch(`http://localhost:8000/auth/check?shop=${shop}`, {
        credentials: "include",
      });
      if (!res.ok) return false;
      const data = await res.json();
      return data?.authenticated ?? false;
    } catch (err) {
      return false;
    }
  }
  