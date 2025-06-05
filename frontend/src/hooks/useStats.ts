import { useQuery } from '@tanstack/react-query';
import { getProcessingStats, getResourceStats } from '../services/api';
import { ProcessingStats, ResourceStats } from '../types/stats';

export function useStats() {
  const {
    data: processingStats,
    isLoading: isLoadingProcessing,
    error: processingError
  } = useQuery<ProcessingStats>({
    queryKey: ['processing-stats'],
    queryFn: getProcessingStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const {
    data: resourceStats,
    isLoading: isLoadingResources,
    error: resourceError
  } = useQuery<ResourceStats>({
    queryKey: ['resource-stats'],
    queryFn: getResourceStats,
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  return {
    processingStats,
    resourceStats,
    isLoading: isLoadingProcessing || isLoadingResources,
    error: processingError || resourceError
  };
} 