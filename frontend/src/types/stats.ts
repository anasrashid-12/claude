export interface ProcessingStats {
  total_processed: number;
  success_rate: number;
  average_processing_time: number;
  total_storage_used: number;
  images_per_hour: number;
}

export interface ResourceStats {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  queue_size: number;
  active_workers: number;
} 