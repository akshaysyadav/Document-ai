import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Document API endpoints
export const documentAPI = {
  // Get all documents with pagination and search
  getDocuments: async (params = {}) => {
    const { page = 1, size = 10, search = '' } = params;
    const skip = (page - 1) * size;
    const response = await api.get('/api/documents/', {
      params: { skip, limit: size, search: search || undefined }
    });
    return response.data;
  },

  // Get single document by ID
  getDocument: async (id) => {
    const response = await api.get(`/api/documents/${id}`);
    return response.data;
  },

  // Create new document
  createDocument: async (documentData) => {
    const formData = new FormData();
    
    // Add text fields
    formData.append('title', documentData.title);
    if (documentData.description) formData.append('description', documentData.description);
    if (documentData.content) formData.append('content', documentData.content);
    if (documentData.tags && documentData.tags.length > 0) {
      formData.append('tags', JSON.stringify(documentData.tags));
    }
    
    // Add file if present
    if (documentData.file) {
      formData.append('file', documentData.file);
    }

    const response = await api.post('/api/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Update document
  updateDocument: async (id, documentData) => {
    const formData = new FormData();
    
    // Add text fields (only if they exist)
    if (documentData.title !== undefined) formData.append('title', documentData.title);
    if (documentData.description !== undefined) formData.append('description', documentData.description);
    if (documentData.content !== undefined) formData.append('content', documentData.content);
    if (documentData.tags !== undefined) {
      formData.append('tags', JSON.stringify(documentData.tags));
    }
    
    // Add file if present
    if (documentData.file) {
      formData.append('file', documentData.file);
    }

    const response = await api.put(`/api/documents/${id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete document
  deleteDocument: async (id) => {
    const response = await api.delete(`/api/documents/${id}`);
    return response.data;
  },

  // Download file
  downloadFile: async (id, filename) => {
    const response = await api.get(`/api/documents/${id}/download`, {
      responseType: 'blob',
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // Search documents
  searchDocuments: async (query, limit = 10) => {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('limit', limit.toString());

    const response = await api.post('/api/documents/search', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Upload file only
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/api/documents/health');
    return response.data;
  },

  // Get document results (summary, chunks, tasks)
  getDocumentResults: async (documentId) => {
    const response = await api.get(`/api/documents/${documentId}/results`);
    return response.data;
  },

  // Reprocess document
  reprocessDocument: async (documentId) => {
    const response = await api.post(`/api/documents/${documentId}/reprocess`);
    return response.data;
  },

  // Update task
  updateTask: async (taskId, updates) => {
    const response = await api.patch(`/api/tasks/${taskId}`, updates);
    return response.data;
  },
};

// General API utilities
export const apiUtils = {
  // Check if API is available
  isApiAvailable: async () => {
    try {
      await api.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  },

  // Get API health status
  getHealthStatus: async () => {
    try {
      const response = await api.get('/health');
      return { status: 'healthy', data: response.data };
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  },
};

export default api;