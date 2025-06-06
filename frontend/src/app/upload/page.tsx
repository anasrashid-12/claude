import React, { useState, useCallback } from 'react';
import {
  Page,
  Layout,
  Card,
  Text,
  Button,
  BlockStack,
  Box,
  DropZone,
  Thumbnail,
  Banner,
  ProgressBar,
  InlineStack,
  ChoiceList
} from '@shopify/polaris';
import { NoteMinor } from '@shopify/polaris-icons';

interface UploadFile extends File {
  id: string;
  preview?: string;
  progress?: number;
  error?: string;
}

export default function UploadPage() {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [processingTypes, setProcessingTypes] = useState<string[]>(['background_removal']);
  const [isUploading, setIsUploading] = useState(false);

  const handleDrop = useCallback(
    (_droppedFiles: File[], acceptedFiles: File[], _rejectedFiles: File[]) => {
      const newFiles = acceptedFiles.map((file) => ({
        ...file,
        id: Math.random().toString(36).substring(7),
        preview: URL.createObjectURL(file),
        progress: 0
      }));

      setFiles((currentFiles) => [...currentFiles, ...newFiles]);
    },
    []
  );

  const handleRemove = useCallback((fileId: string) => {
    setFiles((currentFiles) => {
      const updatedFiles = currentFiles.filter((file) => file.id !== fileId);
      const removedFile = currentFiles.find((file) => file.id === fileId);
      if (removedFile?.preview) {
        URL.revokeObjectURL(removedFile.preview);
      }
      return updatedFiles;
    });
  }, []);

  const handleUpload = async () => {
    setIsUploading(true);

    try {
      // Simulate file upload with progress
      for (const file of files) {
        for (let progress = 0; progress <= 100; progress += 10) {
          setFiles((currentFiles) =>
            currentFiles.map((f) =>
              f.id === file.id ? { ...f, progress } : f
            )
          );
          await new Promise((resolve) => setTimeout(resolve, 200));
        }
      }

      // TODO: Implement actual file upload and processing
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Clear files after successful upload
      setFiles([]);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const validImageTypes = ['image/jpeg', 'image/png', 'image/gif'];

  return (
    <Page
      title="Upload Images"
      primaryAction={
        <Button
          variant="primary"
          onClick={handleUpload}
          loading={isUploading}
          disabled={files.length === 0}
        >
          Process Images
        </Button>
      }
    >
      <BlockStack>
        <Layout>
          <Layout.Section>
            <Card>
              <Box padding="3">
                <BlockStack>
                  <DropZone
                    accept="image/*"
                    type="image"
                    onDrop={handleDrop}
                    allowMultiple
                    errorOverlayText="File type must be .jpg, .png or .gif"
                  >
                    <DropZone.FileUpload actionHint="or drop files to upload" />
                  </DropZone>

                  {files.length > 0 && (
                    <BlockStack>
                      {files.map((file) => (
                        <Card key={file.id}>
                          <Box padding="3">
                            <InlineStack align="space-between">
                              <InlineStack>
                                <div style={{ width: '50px', flexShrink: 0 }}>
                                  <Thumbnail
                                    source={file.preview || NoteMinor}
                                    alt={file.name}
                                  />
                                </div>
                                <BlockStack>
                                  <Text as="span" variant="bodySm" fontWeight="bold">
                                    {file.name}
                                  </Text>
                                  <Text as="span" variant="bodySm">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                  </Text>
                                </BlockStack>
                              </InlineStack>
                              <Button
                                variant="plain"
                                onClick={() => handleRemove(file.id)}
                                disabled={isUploading}
                              >
                                Remove
                              </Button>
                            </InlineStack>
                            {typeof file.progress === 'number' && file.progress > 0 && (
                              <Box paddingBlockStart="3">
                                <ProgressBar
                                  progress={file.progress}
                                  size="small"
                                />
                              </Box>
                            )}
                          </Box>
                        </Card>
                      ))}
                    </BlockStack>
                  )}
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          <Layout.Section>
            <Card>
              <Box padding="3">
                <BlockStack>
                  <Text as="h2" variant="headingMd">
                    Processing Options
                  </Text>

                  <ChoiceList
                    title="Select processing types"
                    allowMultiple
                    choices={[
                      { label: 'Background Removal', value: 'background_removal' },
                      { label: 'Image Optimization', value: 'optimization' },
                      { label: 'Auto Resize', value: 'resize' }
                    ]}
                    selected={processingTypes}
                    onChange={setProcessingTypes}
                  />
                </BlockStack>
              </Box>
            </Card>
          </Layout.Section>

          {files.length > 0 && (
            <Layout.Section>
              <Banner title="Ready to process">
                <p>
                  {files.length} image{files.length === 1 ? '' : 's'} selected for processing.
                  Click "Process Images" to start.
                </p>
              </Banner>
            </Layout.Section>
          )}
        </Layout>
      </BlockStack>
    </Page>
  );
} 