"use client";
import { useEffect } from "react";

export default function LoginPage() {
  useEffect(() => {
    const shop = new URLSearchParams(window.location.search).get("shop");

    if (shop) {
      const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "https://6a8a-2400-adc1-47c-4e00-f584-ac49-1130-c0fb.ngrok-free.app";
      window.location.replace(`${backendBaseUrl}/auth/install?shop=${shop}`);
    }
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-xl font-medium">Redirecting to Shopify login...</p>
    </div>
  );
}
