'use client';

import { ReactNode } from 'react';
import AppBridgeProvider from '@/components/AppBridgeProvider';

export default function AuthLayout({ children }: { children: ReactNode }) {
  return <AppBridgeProvider>{children}</AppBridgeProvider>;
}
