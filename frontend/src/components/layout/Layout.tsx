import React from 'react';
import { Frame, Navigation } from '@shopify/polaris';
import { 
  HomeMinor, 
  ImagesMajor,
  SettingsMajor,
  AnalyticsMajor 
} from '@shopify/polaris-icons';
import Header from './Header';
import { useRouter } from 'next/router';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();

  const navigationItems = [
    {
      label: 'Dashboard',
      icon: HomeMinor,
      url: '/dashboard',
      selected: router.pathname === '/dashboard',
    },
    {
      label: 'Image Gallery',
      icon: ImagesMajor,
      url: '/gallery',
      selected: router.pathname === '/gallery',
    },
    {
      label: 'Analytics',
      icon: AnalyticsMajor,
      url: '/analytics',
      selected: router.pathname === '/analytics',
    },
    {
      label: 'Settings',
      icon: SettingsMajor,
      url: '/settings',
      selected: router.pathname === '/settings',
    },
  ];

  return (
    <Frame
      navigation={<Navigation location="/" items={navigationItems} />}
      topBar={<Header />}
    >
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </Frame>
  );
} 