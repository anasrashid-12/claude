export interface QueueItem {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  position: number;
  created_at: string;
  estimated_time: number;
}

export interface QueueStatus {
  active_jobs: number;
  pending_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  average_processing_time: number;
  jobs?: QueueItem[];
} 