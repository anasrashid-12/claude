import React from 'react';
import { Navigation as PolarisNavigation } from '@shopify/polaris';
import {
  HomeMinor,
  ImagesMajor,
  UploadMajor,
  SettingsMajor,
  AnalyticsMajor
} from '@shopify/polaris-icons';
import { usePathname } from 'next/navigation';
import { useRouter } from 'next/router';

export function Navigation() {
  const pathname = usePathname();
  const router = useRouter();

  const navigationItems = [
    {
      label: 'Dashboard',
      icon: HomeMinor,
      url: '/dashboard',
      selected: pathname === '/dashboard',
      onClick: () => router.push('/dashboard')
    },
    {
      label: 'Image Gallery',
      icon: ImagesMajor,
      url: '/gallery',
      selected: pathname === '/gallery',
      onClick: () => router.push('/gallery')
    },
    {
      label: 'Upload',
      icon: UploadMajor,
      url: '/upload',
      selected: pathname === '/upload',
      onClick: () => router.push('/upload')
    },
    {
      label: 'Analytics',
      icon: AnalyticsMajor,
      url: '/analytics',
      selected: pathname === '/analytics',
      onClick: () => router.push('/analytics')
    },
    {
      label: 'Settings',
      icon: SettingsMajor,
      url: '/settings',
      selected: pathname === '/settings',
      onClick: () => router.push('/settings')
    }
  ];

  return (
    <PolarisNavigation location={pathname}>
      <PolarisNavigation.Section items={navigationItems} />
    </PolarisNavigation>
  );
} 