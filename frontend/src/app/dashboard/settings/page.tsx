'use client';

import { useState } from 'react';

interface Settings {
  notifications: boolean;
  autoProcessing: boolean;
  maxFileSize: number;
  allowedFileTypes: string[];
  defaultSortOrder: 'asc' | 'desc';
  defaultView: 'grid' | 'list';
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>({
    notifications: true,
    autoProcessing: true,
    maxFileSize: 10,
    allowedFileTypes: ['.jpg', '.jpeg', '.png', '.gif'],
    defaultSortOrder: 'desc',
    defaultView: 'grid'
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveMessage('');

    try {
      // TODO: Implement actual settings update API call
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setSaveMessage('Settings saved successfully!');
    } catch (error) {
      setSaveMessage('Error saving settings. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleFileTypeChange = (type: string) => {
    setSettings((prev) => ({
      ...prev,
      allowedFileTypes: prev.allowedFileTypes.includes(type)
        ? prev.allowedFileTypes.filter((t) => t !== type)
        : [...prev.allowedFileTypes, type]
    }));
  };

  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Settings</h3>
          <form onSubmit={handleSubmit} className="mt-6 space-y-6">
            {/* Notifications */}
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="notifications"
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) =>
                    setSettings((prev) => ({
                      ...prev,
                      notifications: e.target.checked
                    }))
                  }
                  className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="notifications" className="font-medium text-gray-700">
                  Email Notifications
                </label>
                <p className="text-gray-500">
                  Receive notifications when file processing is complete
                </p>
              </div>
            </div>

            {/* Auto Processing */}
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="autoProcessing"
                  type="checkbox"
                  checked={settings.autoProcessing}
                  onChange={(e) =>
                    setSettings((prev) => ({
                      ...prev,
                      autoProcessing: e.target.checked
                    }))
                  }
                  className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
              </div>
              <div className="ml-3 text-sm">
                <label htmlFor="autoProcessing" className="font-medium text-gray-700">
                  Auto Processing
                </label>
                <p className="text-gray-500">
                  Automatically process files after upload
                </p>
              </div>
            </div>

            {/* Max File Size */}
            <div>
              <label htmlFor="maxFileSize" className="block text-sm font-medium text-gray-700">
                Maximum File Size (MB)
              </label>
              <input
                type="number"
                id="maxFileSize"
                value={settings.maxFileSize}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    maxFileSize: Number(e.target.value)
                  }))
                }
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            {/* Allowed File Types */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Allowed File Types
              </label>
              <div className="mt-2 space-x-4">
                {['.jpg', '.jpeg', '.png', '.gif'].map((type) => (
                  <label key={type} className="inline-flex items-center">
                    <input
                      type="checkbox"
                      checked={settings.allowedFileTypes.includes(type)}
                      onChange={() => handleFileTypeChange(type)}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">{type}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Default Sort Order */}
            <div>
              <label htmlFor="defaultSort" className="block text-sm font-medium text-gray-700">
                Default Sort Order
              </label>
              <select
                id="defaultSort"
                value={settings.defaultSortOrder}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    defaultSortOrder: e.target.value as 'asc' | 'desc'
                  }))
                }
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>

            {/* Default View */}
            <div>
              <label htmlFor="defaultView" className="block text-sm font-medium text-gray-700">
                Default View
              </label>
              <select
                id="defaultView"
                value={settings.defaultView}
                onChange={(e) =>
                  setSettings((prev) => ({
                    ...prev,
                    defaultView: e.target.value as 'grid' | 'list'
                  }))
                }
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="grid">Grid</option>
                <option value="list">List</option>
              </select>
            </div>

            {/* Save Button */}
            <div className="flex items-center justify-end space-x-4">
              {saveMessage && (
                <p
                  className={`text-sm ${
                    saveMessage.includes('Error') ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  {saveMessage}
                </p>
              )}
              <button
                type="submit"
                disabled={isSaving}
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                  isSaving ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {isSaving ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 