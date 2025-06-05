import { useCallback } from 'react';
import { DropZone, Stack, Thumbnail, Caption } from '@shopify/polaris';

interface ImageUploaderProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

export function ImageUploader({ onFileSelect, selectedFile }: ImageUploaderProps) {
  const handleDrop = useCallback(
    (_dropFiles: File[], acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const validImageTypes = ['image/jpeg', 'image/png', 'image/webp'];

  return (
    <Stack vertical>
      <DropZone
        accept={validImageTypes.join(',')}
        onDrop={handleDrop}
        allowMultiple={false}
      >
        <DropZone.FileUpload />
      </DropZone>
      {selectedFile && (
        <Stack alignment="center">
          <Thumbnail
            source={URL.createObjectURL(selectedFile)}
            alt={selectedFile.name}
            size="large"
          />
          <div>
            <Caption>{selectedFile.name}</Caption>
            <Caption>{Math.round(selectedFile.size / 1024)} KB</Caption>
          </div>
        </Stack>
      )}
    </Stack>
  );
} 