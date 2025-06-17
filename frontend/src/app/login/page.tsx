'use client';

import { useState } from 'react';
import { Page, Layout, TextField, Button, Card, Box, Text, Banner } from '@shopify/polaris';

export default function LoginPage() {
  const [shop, setShop] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = () => {
    if (!shop || !shop.endsWith('.myshopify.com')) {
      setError('Please enter a valid Shopify store like "example.myshopify.com"');
      return;
    }

    setError('');
    setLoading(true);
    window.location.href = `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/install?shop=${encodeURIComponent(shop)}`;
  };

  return (
    <Page title="Maxflow Image App - Login">
      <Layout>
        <Layout.Section>
          <Card>
            <Box padding="400">
              <Text as="h2" variant="headingMd">
                Connect your Shopify store
              </Text>

              <div style={{ marginTop: '1rem' }}>
                <TextField
                  label="Enter your Shopify store domain"
                  value={shop}
                  onChange={setShop}
                  autoComplete="off"
                  placeholder="example.myshopify.com"
                />
              </div>

              {error && (
                <div style={{ marginTop: '1rem' }}>
                  <Banner tone="critical">{error}</Banner>
                </div>
              )}

              <div style={{ marginTop: '1rem' }}>
                <Button onClick={handleLogin} loading={loading} variant="primary">
                  Connect Store
                </Button>
              </div>
            </Box>
          </Card>
        </Layout.Section>
      </Layout>
    </Page>
  );
}
