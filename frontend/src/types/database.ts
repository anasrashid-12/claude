export type ProcessingStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ImageOperation = 'background_removal' | 'resize' | 'optimize' | 'revert';

export interface Store {
  id: string;
  shop_domain: string;
  access_token: string | null;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  plan_type: string | null;
  api_usage_count: number;
  last_sync_at: string | null;
}

export interface Product {
  id: string;
  store_id: string;
  shopify_product_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  last_processed_at: string | null;
}

export interface Image {
  id: string;
  product_id: string;
  shopify_image_id: string;
  original_url: string;
  current_url: string;
  position: number | null;
  width: number | null;
  height: number | null;
  format: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProcessingHistory {
  id: string;
  image_id: string;
  operation: ImageOperation;
  status: ProcessingStatus;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
  settings: Record<string, any> | null;
  backup_url: string | null;
  created_at: string;
}

export interface ImageVersion {
  id: string;
  image_id: string;
  version_number: number;
  storage_url: string;
  created_at: string;
  processing_history_id: string | null;
}

export interface StoreSettings {
  id: string;
  store_id: string;
  default_image_settings: Record<string, any>;
  auto_process_new_images: boolean;
  notification_email: string | null;
  created_at: string;
  updated_at: string;
}

// Helper type for pagination
export interface PaginatedResponse<T> {
  data: T[];
  count: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
} 