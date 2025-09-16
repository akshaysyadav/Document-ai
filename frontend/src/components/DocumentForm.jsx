import React, { useState, useEffect, useRef } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { X, Upload, File, Trash2 } from 'lucide-react';
import { documentAPI } from '../services/api';

const DocumentForm = ({ document, onClose, onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    content: '',
    tags: [],
    file: null
  });
  const [loading, setLoading] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  // Initialize form with document data if editing
  useEffect(() => {
    if (document) {
      setFormData({
        title: document.title || '',
        description: document.description || '',
        content: document.content || '',
        tags: document.tags || [],
        file: null // File is not pre-loaded for editing
      });
    }
  }, [document]);

  // Handle input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle tag management
  const addTag = (e) => {
    e.preventDefault();
    const tag = tagInput.trim();
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  // Handle file upload
  const handleFileChange = (file) => {
    if (file) {
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        onError('File size must be less than 10MB');
        return;
      }
      
      setFormData(prev => ({
        ...prev,
        file
      }));
    }
  };

  // Handle drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileChange(files[0]);
    }
  };

  // Remove file
  const removeFile = () => {
    setFormData(prev => ({
      ...prev,
      file: null
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.title.trim()) {
      onError('Title is required');
      return;
    }

    setLoading(true);
    
    try {
      if (document) {
        // Update existing document
        await documentAPI.updateDocument(document.id, formData);
      } else {
        // Create new document
        await documentAPI.createDocument(formData);
      }
      
      onSuccess();
    } catch (err) {
      onError(`Failed to ${document ? 'update' : 'create'} document: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-background border border-border rounded-xl w-full max-w-3xl max-h-[90vh] overflow-auto shadow-2xl">
        <div className="p-8 space-y-8">
          {/* Header */}
          <div className="flex justify-between items-center pb-6 border-b border-border">
            <div>
              <h2 className="text-3xl font-display font-bold text-foreground">
                {document ? 'Edit Document' : 'Create New Document'}
              </h2>
              <p className="text-muted-foreground mt-2">
                {document ? 'Update your document information and content' : 'Add a new document to your collection'}
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose} className="hover:bg-primary/10">
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Title */}
            <div className="space-y-3">
              <Label htmlFor="title" className="text-base font-semibold text-foreground">Title *</Label>
              <Input
                id="title"
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter document title"
                required
                className="h-12 text-base border-border/50 focus:border-primary"
              />
            </div>

            {/* Description */}
            <div className="space-y-3">
              <Label htmlFor="description" className="text-base font-semibold text-foreground">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Enter document description"
                rows={3}
                className="text-base border-border/50 focus:border-primary resize-none"
              />
            </div>

            {/* Content */}
            <div className="space-y-3">
              <Label htmlFor="content" className="text-base font-semibold text-foreground">Content</Label>
              <Textarea
                id="content"
                value={formData.content}
                onChange={(e) => handleInputChange('content', e.target.value)}
                placeholder="Enter document content"
                rows={6}
                className="text-base border-border/50 focus:border-primary resize-none"
              />
            </div>

            {/* Tags */}
            <div className="space-y-3">
              <Label className="text-base font-semibold text-foreground">Tags</Label>
              <div className="flex gap-3">
                <Input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  placeholder="Add a tag"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      addTag(e);
                    }
                  }}
                  className="h-12 text-base border-border/50 focus:border-primary"
                />
                <Button type="button" onClick={addTag} variant="outline" className="h-12 px-6 border-primary/20 hover:bg-primary/10">
                  Add Tag
                </Button>
              </div>
              
              {/* Display tags */}
              {formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {formData.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary" className="flex items-center gap-2 bg-primary/10 text-primary border-primary/20 px-3 py-1">
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="ml-1 hover:text-destructive transition-colors"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {/* File Upload */}
            <div className="space-y-3">
              <Label className="text-base font-semibold text-foreground">File Attachment</Label>
              
              {/* Current file from existing document */}
              {document && document.file_name && !formData.file && (
                <div className="bg-primary/5 border border-primary/20 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <File className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <span className="text-base font-medium text-foreground">{document.file_name}</span>
                        <span className="text-sm text-muted-foreground ml-2">
                          ({formatFileSize(document.file_size)})
                        </span>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-primary/10 text-primary">Current file</Badge>
                  </div>
                </div>
              )}

              {/* File drop zone */}
              {!formData.file && (
                <div
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer ${
                    dragOver
                      ? 'border-primary bg-primary/5 scale-[1.02]'
                      : 'border-border hover:border-primary/50 hover:bg-primary/5'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current && fileInputRef.current.click()}
                >
                  <div className="p-4 rounded-full bg-primary/10 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <Upload className="w-8 h-8 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground mb-2">
                    Drop your file here
                  </h3>
                  <p className="text-muted-foreground mb-4">
                    Drag and drop a file here, or click to browse
                  </p>
                  <input
                    type="file"
                    onChange={(e) => handleFileChange(e.target.files[0])}
                    className="hidden"
                    id="file-upload"
                    accept=".pdf,.doc,.docx,.txt,.md,.jpg,.jpeg,.png,.gif"
                    ref={fileInputRef}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="lg"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      if (fileInputRef.current) fileInputRef.current.click();
                    }}
                    className="border-primary/20 hover:bg-primary/10"
                  >
                    Choose File
                  </Button>
                  <p className="text-sm text-muted-foreground mt-4">
                    Maximum file size: 10MB • Supports PDF, DOC, TXT, MD, Images
                  </p>
                </div>
              )}

              {/* Selected file preview */}
              {formData.file && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-green-100">
                        <File className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <span className="text-base font-medium text-green-800">{formData.file.name}</span>
                        <span className="text-sm text-green-600 ml-2">
                          ({formatFileSize(formData.file.size)})
                        </span>
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={removeFile}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* Form Actions */}
            <div className="flex justify-end gap-4 pt-8 border-t border-border">
              <Button type="button" variant="outline" onClick={onClose} size="lg" className="px-8 border-border hover:bg-muted">
                Cancel
              </Button>
              <Button type="submit" disabled={loading} size="lg" className="px-8 bg-primary text-white hover:bg-primary/90">
                {loading ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    {document ? 'Updating...' : 'Creating...'}
                  </div>
                ) : (
                  <>
                    {document ? 'Update Document' : 'Create Document'}
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default DocumentForm;