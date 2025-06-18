'use client';

import { useState } from 'react';
import {
  Page,
  Text,
  TextField,
  Button,
  Card,
  Box,
  InlineError,
} from '@shopify/polaris';

export default function LoginPage() {
  const [shop, setShop] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const input = shop.trim().toLowerCase();
    const shopDomain = input.endsWith('.myshopify.com')
      ? input
      : `${input}.myshopify.com`;

    const isValid = /^[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com$/.test(shopDomain);
    if (!isValid) {
      setError('Please enter a valid Shopify store like "example" or "example.myshopify.com"');
      return;
    }

    setLoading(true);
    try {
      const installUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL}/auth/install?shop=${encodeURIComponent(shopDomain)}`;
      window.location.href = installUrl;
    } catch (err) {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Page>
      <div className="max-w-md mx-auto pt-40">
        <Card padding="300" roundedAbove="sm">
          <form onSubmit={handleSubmit}>
            <Text as="h1" variant="headingLg" alignment="center">
              Enter Your Shopify Store
            </Text>

            <Box paddingBlockStart="200">
              <TextField
                label="Shop Domain"
                placeholder="example or example.myshopify.com"
                value={shop}
                onChange={setShop}
                autoComplete="off"
                error={error ? <InlineError message={error} fieldID="shop" /> : undefined}
              />
            </Box>

            <div className="pt-6 flex justify-center">
              <Button submit variant="primary" loading={loading} disabled={!shop}>
                Continue
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </Page>
  );
}
