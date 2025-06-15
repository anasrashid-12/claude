/* frontend/app/login/page.tsx */
'use client';

import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { Page, Layout, TextField, Button, Card } from '@shopify/polaris';

export default function LoginPage() {
  const router = useRouter();
  const [shop, setShop] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = () => {
    if (!shop) return;
    setLoading(true);
    router.push(`http://localhost:8000/auth/install?shop=${encodeURIComponent(shop)}`);
  };

  return (
    <Page title="Maxflow Image App - Login">
      <Layout>
        <Layout.Section>
          <Card sectioned>
            <TextField
              label="Enter your Shopify store domain"
              value={shop}
              onChange={setShop}
              autoComplete="off"
              placeholder="example.myshopify.com"
            />
            <div style={{ marginTop: '1rem' }}>
              <Button onClick={handleLogin} loading={loading} primary>
                Connect Store
              </Button>
            </div>
          </Card>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
