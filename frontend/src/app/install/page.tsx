'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Page,
  Layout,
  Card,
  FormLayout,
  TextField,
  Button,
  Text,
  Banner,
  BlockStack,
} from '@shopify/polaris';

export default function InstallPage() {
  const [shop, setShop] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Basic validation
    if (!shop) {
      setError('Please enter your shop domain');
      return;
    }

    // Format the shop domain
    let formattedShop = shop.toLowerCase().trim();
    if (!formattedShop.includes('.myshopify.com')) {
      formattedShop += '.myshopify.com';
    }

    // Validate shop format
    if (!formattedShop.match(/^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$/)) {
      setError('Please enter a valid Shopify shop domain');
      return;
    }

    // Redirect to auth with the shop parameter
    router.push(`/api/auth?shop=${formattedShop}`);
  };

  return (
    <Page>
      <Layout>
        <Layout.Section>
          <BlockStack gap="500">
            <Card>
              <BlockStack gap="400">
                <Text as="h1" variant="headingLg">
                  Install AI Image Processing App
                </Text>
                
                <Text as="p" variant="bodyMd">
                  To get started, please enter your Shopify store domain.
                </Text>

                {error && (
                  <Banner tone="critical">
                    <p>{error}</p>
                  </Banner>
                )}

                <form onSubmit={handleSubmit}>
                  <FormLayout>
                    <TextField
                      label="Shop Domain"
                      type="text"
                      value={shop}
                      onChange={setShop}
                      autoComplete="off"
                      placeholder="your-store.myshopify.com"
                      helpText="Enter your Shopify store domain (e.g., your-store.myshopify.com)"
                    />
                    <Button variant="primary" submit>
                      Install App
                    </Button>
                  </FormLayout>
                </form>
              </BlockStack>
            </Card>
          </BlockStack>
        </Layout.Section>
      </Layout>
    </Page>
  );
} 