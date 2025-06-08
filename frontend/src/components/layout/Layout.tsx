import React from 'react';
import { Frame, Navigation, TopBar, AppProvider } from '@shopify/polaris';
import { NavigationMenu } from '@shopify/app-bridge-react';
import { HomeIcon, ImageIcon, SettingsIcon, AnalyticsIcon } from '@shopify/polaris-icons';
import { useRouter } from 'next/router';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();

  const navigationItems = [
    {
      label: 'Home',
      destination: '/',
      icon: HomeIcon,
    },
    {
      label: 'Image Gallery',
      destination: '/gallery',
      icon: ImageIcon,
    },
    {
      label: 'Processing Queue',
      destination: '/queue',
      icon: ProcessingQueueIcon,
    },
    {
      label: 'Analytics',
      destination: '/analytics',
      icon: AnalyticsIcon,
    },
    {
      label: 'Settings',
      destination: '/settings',
      icon: SettingsIcon,
    },
  ];

  return (
    <AppProvider i18n={{}}>
      <Frame
        navigation={
          <Navigation location={router.pathname}>
            <NavigationMenu 
              navigationItems={navigationItems}
              matcher={(link) => router.pathname === link.destination}
            />
          </Navigation>
        }
        topBar={
          <TopBar
            showNavigationToggle
            userMenu={
              <TopBar.UserMenu
                name="Store Owner"
                detail="My Store"
                initials="SO"
              />
            }
          />
        }
      >
        <div className="app-content">
          {children}
        </div>
      </Frame>
    </AppProvider>
  );
} 