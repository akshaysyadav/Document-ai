import React, { useState } from 'react';
import { documentAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

export const UploadPanel = ({ onDocumentUploaded }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    tags: '',
    file: null,
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { toast } = useToast();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (file.type !== 'application/pdf') {
        toast({
          title: "Invalid file type",
          description: "Please upload a PDF file only.",
          variant: "destructive",
        });
        return;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: "File too large",
          description: "Please upload a file smaller than 10MB.",
          variant: "destructive",
        });
        return;
      }

      setFormData(prev => ({
        ...prev,
        file: file
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      toast({
        title: "Title required",
        description: "Please enter a title for the document.",
        variant: "destructive",
      });
      return;
    }

    if (!formData.file) {
      toast({
        title: "File required",
        description: "Please select a PDF file to upload.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Parse tags
      const tagsArray = formData.tags 
        ? formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        : [];

      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      const response = await documentAPI.createDocument({
        title: formData.title,
        description: formData.description,
        tags: tagsArray,
        file: formData.file,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      toast({
        title: "Upload successful",
        description: `Document "${response.title}" has been uploaded and queued for processing.`,
      });

      // Reset form
      setFormData({
        title: '',
        description: '',
        tags: '',
        file: null,
      });
      
      // Clear file input
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';

      // Notify parent component
      if (onDocumentUploaded) {
        onDocumentUploaded();
      }

    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Upload failed",
        description: error.response?.data?.detail || "An error occurred while uploading the document.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleTestDocument = async () => {
    setIsUploading(true);
    setUploadProgress(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      // Create a test document without file
      const response = await documentAPI.createDocument({
        title: 'Test Document',
        description: 'This is a test document for development purposes.',
        tags: ['test', 'development'],
        file: null,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      toast({
        title: "Test document created",
        description: `Test document has been created successfully.`,
      });

      if (onDocumentUploaded) {
        onDocumentUploaded();
      }

    } catch (error) {
      console.error('Test document error:', error);
      toast({
        title: "Test document failed",
        description: error.response?.data?.detail || "An error occurred while creating the test document.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="p-6">
      <div className="max-w-2xl mx-auto">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              Title *
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter document title"
              disabled={isUploading}
              required
            />
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter document description (optional)"
              disabled={isUploading}
            />
          </div>

          {/* Tags */}
          <div>
            <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-2">
              Tags
            </label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter tags separated by commas (optional)"
              disabled={isUploading}
            />
            <p className="text-sm text-gray-500 mt-1">
              Example: safety, maintenance, procedure
            </p>
          </div>

          {/* File Upload */}
          <div>
            <label htmlFor="file-input" className="block text-sm font-medium text-gray-700 mb-2">
              PDF File *
            </label>
            <div className="relative">
              <input
                type="file"
                id="file-input"
                accept=".pdf"
                onChange={handleFileChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                disabled={isUploading}
                required
              />
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Select a PDF file (max 10MB)
            </p>
            {formData.file && (
              <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-700">
                  <strong>Selected:</strong> {formData.file.name} ({(formData.file.size / 1024 / 1024).toFixed(2)} MB)
                </p>
              </div>
            )}
          </div>

          {/* Upload Progress */}
          {isUploading && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={isUploading}
              className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isUploading ? 'Uploading...' : 'Upload Document'}
            </button>
            

          </div>
        </form>

        {/* Instructions */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Upload Instructions</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Upload PDF documents only</li>
            <li>• Maximum file size: 10MB</li>
            <li>• Documents will be automatically processed for NLP analysis</li>
            <li>• Processing status can be tracked in the Documents view</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

