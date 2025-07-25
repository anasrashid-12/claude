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
import { getSupabase } from '../../../../utils/supabaseClient'; // ✅ use shared client

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

  const supabase = getSupabase(); // ✅ reuse shared instance

  useEffect(() => {
    if (!shop) return;

    (async () => {
      try {
        const { data, error: fetchError } = await supabase
          .from('settings')
          .select('*')
          .eq('shop', shop)
          .maybeSingle();

        if (fetchError) {
          setError(fetchError.message);
        } else if (!data) {
          const { error: insertError } = await supabase.from('settings').insert({
            shop,
            background_removal: true,
            optimize_images: true,
            avatar_url: null,
          });
          if (insertError) setError('Insert failed: ' + insertError.message);
          else {
            setBackgroundRemoval(true);
            setOptimizeImages(true);
            setAvatarUrl(null);
          }
        } else {
          setBackgroundRemoval(data.background_removal ?? true);
          setOptimizeImages(data.optimize_images ?? true);
          setAvatarUrl(data.avatar_url ?? null);
        }
      } catch {
        setError('Failed to fetch settings');
      } finally {
        setLoading(false);
      }
    })();
  }, [shop]);

  const handleSave = async () => {
    if (!shop) return;
    setSaving(true);
    try {
      const { error: upsertError } = await supabase.from('settings').upsert({
        shop,
        background_removal: backgroundRemoval,
        optimize_images: optimizeImages,
        avatar_url: avatarUrl,
      });
      if (upsertError) setError(upsertError.message);
      else setToastActive(true);
    } catch {
      setError('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !shop) return;

    const file = e.target.files[0];
    const filePath = `${shop}/avatar-${Date.now()}.${file.name.split('.').pop()}`;

    try {
      const { error: uploadError } = await supabase.storage
        .from('avatars')
        .upload(filePath, file, { upsert: true });

      if (uploadError) {
        setError(uploadError.message);
        return;
      }

      const publicUrl = supabase.storage.from('avatars').getPublicUrl(filePath).data.publicUrl;
      setAvatarUrl(publicUrl);
      setToastActive(true);
    } catch {
      setError('Avatar upload failed');
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
                  onChange={handleAvatarChange}
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
                disabled={!shop || saving}
                className={`bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-5 rounded transition ${(!shop || saving) ? 'opacity-50 cursor-not-allowed' : ''}`}
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
