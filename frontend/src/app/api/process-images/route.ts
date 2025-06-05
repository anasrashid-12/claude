import { NextRequest, NextResponse } from 'next/server';

// Updated route configuration
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
export const maxDuration = 60;

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const files = formData.getAll('files') as File[];
    
    if (!files || files.length === 0) {
      return NextResponse.json(
        { error: 'No files provided' },
        { status: 400 }
      );
    }

    // Get access token from cookie
    const accessToken = req.cookies.get('shopify_access_token')?.value;
    if (!accessToken) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }

    const shop = req.cookies.get('shopify_shop_domain')?.value;
    if (!shop) {
      return NextResponse.json(
        { error: 'Shop not found' },
        { status: 400 }
      );
    }

    const results = [];
    
    for (const file of files) {
      try {
        // Step 1: Create staged upload
        const stagedUploadsQuery = `
          mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
            stagedUploadsCreate(input: $input) {
              stagedTargets {
                resourceUrl
                url
                parameters {
                  name
                  value
                }
              }
              userErrors {
                field
                message
              }
            }
          }
        `;

        const stagedUploadsVariables = {
          input: [{
            filename: file.name,
            mimeType: file.type,
            httpMethod: "POST",
            resource: "IMAGE",
            fileSize: `${file.size}`
          }]
        };

        console.log('Creating staged upload for:', file.name);
        const stagedUploadResponse = await fetch(`https://${shop}/admin/api/2024-01/graphql.json`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': accessToken
          },
          body: JSON.stringify({
            query: stagedUploadsQuery,
            variables: stagedUploadsVariables
          })
        });

        const stagedData = await stagedUploadResponse.json();
        console.log('Staged upload response:', JSON.stringify(stagedData, null, 2));

        if (!stagedUploadResponse.ok) {
          throw new Error(`Failed to create staged upload: ${stagedUploadResponse.statusText}`);
        }

        if (stagedData.errors) {
          throw new Error(`GraphQL errors: ${JSON.stringify(stagedData.errors)}`);
        }
        
        if (!stagedData.data?.stagedUploadsCreate?.stagedTargets?.[0]) {
          throw new Error(`Invalid staged upload response: ${JSON.stringify(stagedData)}`);
        }

        const target = stagedData.data.stagedUploadsCreate.stagedTargets[0];

        // Step 2: Upload to staged target
        console.log('Uploading to staged target:', target.url);
        const buffer = await file.arrayBuffer();
        const uploadFormData = new FormData();
        
        // Add parameters from staged upload
        target.parameters.forEach((param: { name: string; value: string }) => {
          uploadFormData.append(param.name, param.value);
        });

        // Add the file with a specific name
        uploadFormData.append('file', new Blob([buffer], { type: file.type }), file.name);

        const uploadResponse = await fetch(target.url, {
          method: 'POST',
          body: uploadFormData
        });

        if (!uploadResponse.ok) {
          const uploadErrorText = await uploadResponse.text();
          throw new Error(`Failed to upload to staged target: ${uploadResponse.status} ${uploadResponse.statusText}\n${uploadErrorText}`);
        }

        // Step 3: Create the file in Shopify
        const createFileQuery = `
          mutation fileCreate($files: [FileCreateInput!]!) {
            fileCreate(files: $files) {
              files {
                id
                alt
                createdAt
                fileStatus
                preview {
                  image {
                    originalSrc
                  }
                }
              }
              userErrors {
                field
                message
              }
            }
          }
        `;

        const createFileVariables = {
          files: [{
            alt: file.name,
            contentType: "IMAGE",
            originalSource: target.resourceUrl
          }]
        };

        console.log('Creating file with:', JSON.stringify(createFileVariables, null, 2));
        const createFileResponse = await fetch(`https://${shop}/admin/api/2024-01/graphql.json`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': accessToken
          },
          body: JSON.stringify({
            query: createFileQuery,
            variables: createFileVariables
          })
        });

        const fileData = await createFileResponse.json();
        console.log('File creation response:', JSON.stringify(fileData, null, 2));

        if (!createFileResponse.ok) {
          throw new Error(`Failed to create file: ${createFileResponse.statusText}`);
        }

        if (fileData.errors) {
          throw new Error(`GraphQL errors: ${JSON.stringify(fileData.errors)}`);
        }

        if (!fileData.data?.fileCreate?.files?.[0]) {
          throw new Error(`Invalid file creation response: ${JSON.stringify(fileData)}`);
        }

        const createdFile = fileData.data.fileCreate.files[0];
        
        // Poll for file status if it's not ready
        if (createdFile.fileStatus === 'UPLOADED' || createdFile.fileStatus === 'PROCESSING') {
          let fileStatus = createdFile.fileStatus;
          let processedFile = createdFile;
          let attempts = 0;
          const maxAttempts = 10; // Maximum number of polling attempts
          
          const checkFileStatusQuery = `
            query getFile($id: ID!) {
              node(id: $id) {
                ... on File {
                  id
                  fileStatus
                  preview {
                    image {
                      originalSrc
                    }
                  }
                }
              }
            }
          `;

          while ((fileStatus === 'UPLOADED' || fileStatus === 'PROCESSING') && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second between polls
            
            console.log(`Polling file status attempt ${attempts + 1} for file ${file.name}...`);
            const statusResponse = await fetch(`https://${shop}/admin/api/2024-01/graphql.json`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'X-Shopify-Access-Token': accessToken
              },
              body: JSON.stringify({
                query: checkFileStatusQuery,
                variables: { id: createdFile.id }
              })
            });

            const statusData = await statusResponse.json();
            console.log('File status response:', JSON.stringify(statusData, null, 2));

            if (statusData.data?.node) {
              fileStatus = statusData.data.node.fileStatus;
              processedFile = statusData.data.node;
            } else {
              console.error('Failed to get file status:', statusData);
              break;
            }

            attempts++;
          }

          // Update the file data with the processed version if available
          if (fileStatus === 'READY' && processedFile.preview?.image?.originalSrc) {
            createdFile.preview = processedFile.preview;
          }
        }

        results.push({
          originalName: file.name,
          url: createdFile.preview?.image?.originalSrc || target.resourceUrl, // Fallback to staged upload URL if preview not ready
          alt: createdFile.alt,
          id: createdFile.id,
          createdAt: createdFile.createdAt,
          status: createdFile.fileStatus
        });

      } catch (fileError) {
        console.error(`Error processing file ${file.name}:`, fileError);
        results.push({
          originalName: file.name,
          error: fileError instanceof Error ? fileError.message : 'Failed to process file'
        });
      }
    }

    return NextResponse.json({ 
      success: true,
      results 
    });

  } catch (error) {
    console.error('Image processing error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to process images',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

// Increase payload size limit for file uploads
export const config = {
  api: {
    bodyParser: false,
  },
}; 