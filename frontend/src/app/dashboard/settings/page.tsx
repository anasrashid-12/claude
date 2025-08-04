'use client';

import React, { useEffect, useRef, useState } from 'react';
import {
  Text,
  Checkbox,
  Banner,
  Spinner,
  Toast,
  Thumbnail,
  BlockStack,
  InlineStack,
  Divider,
} from '@shopify/polaris';
import useShop from '@/hooks/useShop';

export default function SettingsPage() {
  const { shop, loading: shopLoading } = useShop();
  const [backgroundRemoval, setBackgroundRemoval] = useState(true);
  const [optimizeImages, setOptimizeImages] = useState(true);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [toastActive, setToastActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL;

  useEffect(() => {
    if (!shop) return;

    const fetchSettings = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE_URL}/settings`, {
          credentials: 'include',
        });
        if (!res.ok) throw new Error('Failed to fetch settings');
        const data = await res.json();
        if (data) {
          setBackgroundRemoval(data.background_removal);
          setOptimizeImages(data.optimize_images);
          setAvatarUrl(data.avatar_path);
        }
      } catch (err: any) {
        setError(err?.message || 'Unexpected error');
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, [shop]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE_URL}/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          background_removal: backgroundRemoval,
          optimize_images: optimizeImages,
          avatar_path: avatarUrl,
        }),
      });

      if (!res.ok) throw new Error('Failed to save settings');
      setToastActive(true);
    } catch (err: any) {
      setError(err?.message || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE_URL}/settings/avatar`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (!res.ok) throw new Error('Avatar upload failed');

      const data = await res.json();
      setAvatarUrl(data.url);
      setToastActive(true);
    } catch (err: any) {
      setError(err?.message || 'Avatar upload failed');
    }
  };

  return (
    <div className="px-4 sm:px-6 pt-10 pb-16 max-w-2xl mx-auto text-gray-900 dark:text-white">
      <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">⚙️ App Settings</h1>
      <p className="text-gray-600 dark:text-gray-400 mb-6">
        Manage your preferences and profile avatar.
      </p>

      {loading || shopLoading ? (
        <div className="flex justify-center items-center h-64">
          <Spinner accessibilityLabel="Loading settings" size="large" />
        </div>
      ) : (
        <div className="rounded-xl bg-white dark:bg-[#1e293b] p-6 shadow-lg">
          <BlockStack gap="500">
            <Text as="h2" variant="headingMd" tone="subdued">Preferences</Text>

            <BlockStack gap="300">
              <Checkbox
                label="Remove background from images"
                checked={backgroundRemoval}
                onChange={() => setBackgroundRemoval((prev) => !prev)}
              />
              <Checkbox
                label="Optimize images for web"
                checked={optimizeImages}
                onChange={() => setOptimizeImages((prev) => !prev)}
              />
            </BlockStack>

            <Divider />

            <Text as="h3" variant="headingSm" tone="subdued">Avatar Image</Text>

            <InlineStack align="start" gap="400">
              {avatarUrl && (
                <Thumbnail size="large" source={avatarUrl} alt="Avatar" />
              )}
              <div className="flex flex-col gap-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleAvatarUpload}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded transition"
                >
                  {avatarUrl ? 'Change Avatar' : 'Upload Avatar'}
                </button>
              </div>
            </InlineStack>

            <div className="flex justify-end mt-6">
              <button
                onClick={handleSave}
                disabled={saving}
                className={`bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-5 rounded transition ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {saving ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </BlockStack>
        </div>
      )}

      {error && (
        <div className="mt-4">
          <Banner title="Something went wrong" tone="critical" onDismiss={() => setError(null)}>
            <p>{error}</p>
          </Banner>
        </div>
      )}

      {toastActive && (
        <Toast content="✅ Settings saved successfully" onDismiss={() => setToastActive(false)} />
      )}
    </div>
  );
}
