// app/layout.tsx
import '../styles/globals.css'
import { ReactNode } from 'react'

export const metadata = {
  title: 'Maxflow App',
  description: 'Shopify Image App',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning={true}>
        {children}
      </body>
    </html>
  )
}
