import React, { useState, useCallback } from 'react';
import { TopBar, Button } from '@shopify/polaris';
import { NotificationMajor } from '@shopify/polaris-icons';
import { useRouter } from 'next/router';

export default function Header() {
  const router = useRouter();
  const [userMenuActive, setUserMenuActive] = useState(false);
  const [notificationsActive, setNotificationsActive] = useState(false);

  const toggleUserMenu = useCallback(
    () => setUserMenuActive((active) => !active),
    [],
  );

  const toggleNotifications = useCallback(
    () => setNotificationsActive((active) => !active),
    [],
  );

  const userMenuMarkup = (
    <TopBar.UserMenu
      actions={[
        {
          items: [{
            content: 'Settings',
            onAction: () => router.push('/settings'),
          }]
        },
        {
          items: [{
            content: 'Sign out',
            onAction: () => {/* Handle sign out */},
          }]
        }
      ]}
      name="Store Name"
      detail="Free Plan"
      initials="S"
      open={userMenuActive}
      onToggle={toggleUserMenu}
    />
  );

  const secondaryMenuMarkup = (
    <TopBar.Menu
      activatorContent={
        <Button icon={NotificationMajor} />
      }
      open={notificationsActive}
      onOpen={() => setNotificationsActive(true)}
      onClose={() => setNotificationsActive(false)}
      actions={[
        {
          items: [
            {content: 'No new notifications', disabled: true},
          ],
        },
      ]}
    />
  );

  return (
    <TopBar
      showNavigationToggle
      userMenu={userMenuMarkup}
      secondaryMenu={secondaryMenuMarkup}
    />
  );
} 