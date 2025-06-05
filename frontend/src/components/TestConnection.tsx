import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { SupabaseClient } from '@supabase/supabase-js';

type Bucket = {
  id: string;
  name: string;
  owner: string;
  created_at: string;
  updated_at: string;
  public: boolean;
};

export default function TestConnection() {
  const [status, setStatus] = useState<{
    database: string;
    storage: string;
  }>({
    database: 'Testing...',
    storage: 'Testing...',
  });

  useEffect(() => {
    async function testConnection() {
      try {
        // Test database connection
        const { data, error } = await supabase.from('stores').select('*').limit(1);
        if (error) throw error;
        setStatus(prev => ({ ...prev, database: '✅ Database connection successful!' }));

        // Test storage connection
        const { data: buckets, error: storageError } = await supabase.storage.listBuckets();
        if (storageError) throw storageError;
        
        const hasOriginalBucket = buckets.some((b: Bucket) => b.name === 'original-images');
        const hasProcessedBucket = buckets.some((b: Bucket) => b.name === 'processed-images');

        if (hasOriginalBucket && hasProcessedBucket) {
          setStatus(prev => ({ ...prev, storage: '✅ Storage buckets configured correctly!' }));
        } else {
          setStatus(prev => ({ 
            ...prev, 
            storage: `❌ Missing buckets: ${!hasOriginalBucket ? 'original-images ' : ''}${!hasProcessedBucket ? 'processed-images' : ''}`
          }));
        }
      } catch (error: any) {
        console.error('Connection test failed:', error);
        setStatus({
          database: `❌ Database error: ${error?.message || 'Unknown error'}`,
          storage: `❌ Storage error: ${error?.message || 'Unknown error'}`,
        });
      }
    }

    testConnection();
  }, []);

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Supabase Connection Test</h2>
      <div className="space-y-2">
        <p className="font-mono">{status.database}</p>
        <p className="font-mono">{status.storage}</p>
      </div>
    </div>
  );
} 