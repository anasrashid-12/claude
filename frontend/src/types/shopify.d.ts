declare module '@shopify/shopify-api' {
  export function shopifyApi(config: any): any;
  export const LATEST_API_VERSION: string;
  export class Session {
    id: string;
  }
}

declare module '@shopify/shopify-api/adapters/node' {} 