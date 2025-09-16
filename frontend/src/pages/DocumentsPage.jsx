import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Plus, Search, Download, Edit, Trash2, FileText, Upload, Eye } from 'lucide-react';
import { documentAPI } from '../services/api';
import DocumentForm from '../components/DocumentForm';
import Header from '../components/Header';

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
    <div className="min-h-screen bg-background">
      <Header />
    
      <main className="pt-20">
        {/* Hero Section */}
        <section className="py-8 bg-muted/30">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto text-center">
              <Badge className="mb-4 bg-primary text-white px-6 py-2 text-sm font-medium">
                AI Document Management
              </Badge>
              <h1 className="text-4xl md:text-5xl font-display font-bold mb-4 text-foreground">
                Intelligent Document Processing
              </h1>
              <p className="text-lg text-muted-foreground mb-6 max-w-3xl mx-auto leading-relaxed">
                Transform your metro operations with AI-powered document processing. 
                Automatically scan, extract, and organize all operational documents.
              </p>
            </div>
          </div>
        </section>

        {/* Main Content */}
        <section className="py-6">
          <div className="container mx-auto px-6">
            <div className="max-w-7xl mx-auto space-y-12">
              {/* Search Bar */}
              <form onSubmit={handleSearch} className="mb-12">
                <Card className="border-2 shadow-lg hover:shadow-xl transition-shadow duration-300">
                  <CardContent className="p-8">
                    <div className="flex gap-6">
                      <div className="relative flex-1">
                        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-muted-foreground w-6 h-6" />
                        <Input
                          type="text"
                          placeholder="Search documents, extract data, or ask questions..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="pl-14 h-14 text-lg border-2 focus:border-primary transition-colors"
                        />
                      </div>
                      <Button type="submit" size="lg" className="h-14 px-8 text-lg bg-primary text-white hover:bg-primary/90">
                        Search
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </form>

              {/* Error/Success Messages */}
              {error && (
                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-destructive mb-6">
                  {error}
                </div>
              )}
              {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800 mb-6">
                  {success}
                </div>
              )}

              {/* Documents List */}
              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                </div>
              ) : documents.length === 0 ? (
                <Card className="border-2 shadow-lg">
                  <CardContent className="text-center py-20">
                    <div className="w-20 h-20 rounded-2xl bg-primary text-white flex items-center justify-center mx-auto mb-8">
                      <FileText className="w-10 h-10" />
                    </div>
                    <h3 className="text-3xl font-bold text-foreground mb-6">No documents found</h3>
                    <p className="text-muted-foreground mb-10 text-xl max-w-md mx-auto">
                      {searchTerm ? 'Try adjusting your search terms' : 'Get started by creating your first document'}
                    </p>
                    <Button onClick={() => setShowCreateForm(true)} size="lg" className="bg-primary text-white hover:bg-primary/90 px-8 py-3 text-lg">
                      <Plus className="w-5 h-5 mr-2" />
                      Create Document
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-8">
                  <div className="flex justify-between items-center mb-8">
                    <h2 className="text-3xl font-display font-bold text-foreground">
                      Documents ({documents.length})
                    </h2>
                    <div className="flex items-center gap-4">
                      <Badge variant="secondary" className="text-sm px-4 py-2">
                        Page {currentPage} of {totalPages}
                      </Badge>
                      <Button 
                        onClick={() => setShowCreateForm(true)} 
                        className="bg-primary text-white hover:bg-primary/90"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        New Document
                      </Button>
                    </div>
                  </div>
                  
                  <div className="grid gap-8">
                    {documents.map((document) => (
                      <Card key={document.id} className="border-2 shadow-lg hover:shadow-xl hover:border-primary/50 transition-all duration-300">
                        <CardHeader className="pb-6">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-4 mb-3">
                                <div className="p-3 rounded-xl bg-primary text-white">
                                  <FileText className="w-6 h-6" />
                                </div>
                                <CardTitle className="text-2xl font-bold text-foreground">{document.title}</CardTitle>
                              </div>
                              {document.description && (
                                <CardDescription className="text-lg text-muted-foreground">{document.description}</CardDescription>
                              )}
                            </div>
                            <div className="flex gap-3 ml-6">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setEditingDocument(document)}
                                className="hover:bg-primary hover:text-white transition-colors"
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              {document.file_name && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleDownload(document)}
                                  className="hover:bg-green-600 hover:text-white transition-colors"
                                >
                                  <Download className="w-4 h-4" />
                                </Button>
                              )}
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDelete(document.id)}
                                className="text-destructive hover:bg-destructive hover:text-white transition-colors"
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
                              <div className="bg-muted/30 rounded-lg p-4">
                                <p className="text-sm text-muted-foreground line-clamp-3">
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
                                  <Badge key={index} variant="secondary" className="bg-primary/10 text-primary">
                                    {tag}
                                  </Badge>
                                ))}
                              </div>
                            )}

                            {/* File Info */}
                            {document.file_name && (
                              <div className="flex items-center gap-4 text-sm text-muted-foreground bg-primary/5 rounded-lg p-4">
                                <Upload className="w-4 h-4 text-primary" />
                                <span className="font-medium text-foreground">{document.file_name}</span>
                                <span>({formatFileSize(document.file_size)})</span>
                                <span className="ml-auto">{document.file_type}</span>
                              </div>
                            )}

                            {/* Metadata */}
                            <div className="flex justify-between items-center text-sm text-muted-foreground pt-4 border-t border-border">
                              <span>Created: {formatDate(document.created_at)}</span>
                              {document.updated_at !== document.created_at && (
                                <span>Updated: {formatDate(document.updated_at)}</span>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}</div>
                </div>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <Card className="mt-8">
                  <CardContent className="flex justify-center gap-2 py-6">
                    <Button
                      variant="outline"
                      onClick={() => fetchDocuments(currentPage - 1, searchTerm)}
                      disabled={currentPage === 1}
                      className="border-primary/20 hover:bg-primary/10"
                    >
                      Previous
                    </Button>
                    <span className="flex items-center px-6 py-2 text-sm bg-primary/5 rounded-lg border border-primary/20">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      onClick={() => fetchDocuments(currentPage + 1, searchTerm)}
                      disabled={currentPage === totalPages}
                      className="border-primary/20 hover:bg-primary/10"
                    >
                      Next
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </section>
      </main>

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