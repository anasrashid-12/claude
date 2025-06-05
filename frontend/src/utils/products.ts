import { getShopifyClient } from './shopify';

export async function fetchProducts(accessToken: string, shop: string) {
  const client = getShopifyClient(accessToken, shop);

  const query = `
    query {
      products(first: 10) {
        edges {
          node {
            id
            title
            handle
            description
            images(first: 1) {
              edges {
                node {
                  originalSrc
                  altText
                }
              }
            }
          }
        }
      }
    }
  `;

  const response = await client.graphql(query);
  return response.data.products.edges.map((edge: any) => edge.node);
}

export async function uploadImage(accessToken: string, shop: string, imageData: any) {
  const client = getShopifyClient(accessToken, shop);

  const mutation = `
    mutation fileCreate($input: FileCreateInput!) {
      fileCreate(input: $input) {
        files {
          ... on MediaImage {
            id
            originalSource
            alt
          }
        }
        userErrors {
          field
          message
        }
      }
    }
  `;

  const variables = {
    input: {
      files: [
        {
          alt: imageData.alt || 'Generated image',
          contentType: 'IMAGE',
          originalSource: imageData.url
        }
      ]
    }
  };

  const response = await client.graphql(mutation, variables);
  return response.data.fileCreate;
} 