import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Plus, Search, Download, Edit, Trash2, FileText, Upload } from 'lucide-react';
import { documentAPI } from '../services/api';
import DocumentForm from '../components/DocumentForm';

const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingDocument, setEditingDocument] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch documents
  const fetchDocuments = async (page = 1, search = '') => {
    try {
      setLoading(true);
      const data = await documentAPI.getDocuments({
        page,
        size: 10,
        search
      });
      setDocuments(data.documents);
      setTotalPages(data.pages);
      setCurrentPage(page);
      setError('');
    } catch (err) {
      setError('Failed to fetch documents: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search documents
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchDocuments(1, searchTerm);
  };

  // Delete document
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await documentAPI.deleteDocument(id);
      setSuccess('Document deleted successfully');
      fetchDocuments(currentPage, searchTerm);
    } catch (err) {
      setError('Failed to delete document: ' + err.message);
    }
  };

  // Download file
  const handleDownload = async (document) => {
    if (!document.file_name) {
      setError('No file available for download');
      return;
    }

    try {
      await documentAPI.downloadFile(document.id, document.file_name);
      setSuccess('File download started');
    } catch (err) {
      setError('Failed to download file: ' + err.message);
    }
  };

  // Format file size
  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // Clear messages after 5 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError('');
        setSuccess('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Documents</h1>
            <p className="text-gray-600 mt-1">Manage your documents with AI-powered features</p>
          </div>
          <Button 
            onClick={() => setShowCreateForm(true)}
            className="flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            New Document
          </Button>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="flex-1">
            <Input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <Button type="submit" variant="outline">
            <Search className="w-4 h-4" />
          </Button>
        </form>

        {/* Error/Success Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 text-red-800">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4 text-green-800">
            {success}
          </div>
        )}

        {/* Documents List */}
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : documents.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
              <p className="text-gray-600 mb-4">
                {searchTerm ? 'Try adjusting your search terms' : 'Get started by creating your first document'}
              </p>
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Document
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {documents.map((document) => (
              <Card key={document.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <CardTitle className="text-xl mb-2">{document.title}</CardTitle>
                      {document.description && (
                        <CardDescription>{document.description}</CardDescription>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setEditingDocument(document)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      {document.file_name && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDownload(document)}
                        >
                          <Download className="w-4 h-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(document.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Content Preview */}
                    {document.content && (
                      <div className="bg-gray-50 rounded-md p-3">
                        <p className="text-sm text-gray-700 line-clamp-3">
                          {document.content.length > 200 
                            ? document.content.substring(0, 200) + '...'
                            : document.content
                          }
                        </p>
                      </div>
                    )}

                    {/* Tags */}
                    {document.tags && document.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {document.tags.map((tag, index) => (
                          <Badge key={index} variant="secondary">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}

                    {/* File Info */}
                    {document.file_name && (
                      <div className="flex items-center gap-4 text-sm text-gray-600 bg-blue-50 rounded-md p-3">
                        <Upload className="w-4 h-4" />
                        <span className="font-medium">{document.file_name}</span>
                        <span>({formatFileSize(document.file_size)})</span>
                        <span className="ml-auto">{document.file_type}</span>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="flex justify-between items-center text-sm text-gray-500 pt-2 border-t">
                      <span>Created: {formatDate(document.created_at)}</span>
                      {document.updated_at !== document.created_at && (
                        <span>Updated: {formatDate(document.updated_at)}</span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center gap-2">
            <Button
              variant="outline"
              onClick={() => fetchDocuments(currentPage - 1, searchTerm)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <span className="flex items-center px-4 py-2 text-sm">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              onClick={() => fetchDocuments(currentPage + 1, searchTerm)}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        )}
      </div>

      {/* Create/Edit Forms */}
      {showCreateForm && (
        <DocumentForm
          onClose={() => setShowCreateForm(false)}
          onSuccess={() => {
            setShowCreateForm(false);
            setSuccess('Document created successfully');
            fetchDocuments(currentPage, searchTerm);
          }}
          onError={setError}
        />
      )}

      {editingDocument && (
        <DocumentForm
          document={editingDocument}
          onClose={() => setEditingDocument(null)}
          onSuccess={() => {
            setEditingDocument(null);
            setSuccess('Document updated successfully');
            fetchDocuments(currentPage, searchTerm);
          }}
          onError={setError}
        />
      )}
    </div>
  );
};

export default DocumentsPage;