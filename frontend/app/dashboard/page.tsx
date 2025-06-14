import { redirect } from "next/navigation"; 

export default async function DashboardPage() {
  const shop = "your-shop.myshopify.com"; // Replace dynamically if needed

  const res = await fetch(`http://localhost:8000/auth/check?shop=${shop}`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!res.ok) {
    redirect(`/login?shop=${shop}`);
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <p>Welcome to the dashboard! Authenticated successfully.</p>
    </div>
  );
}
