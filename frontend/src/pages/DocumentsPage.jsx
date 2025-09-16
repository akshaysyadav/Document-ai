import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Plus, Search, Download, Edit, Trash2, FileText, Upload, Eye, Brain, CheckCircle2, Circle, Loader2 } from 'lucide-react';
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
  const [analyzingDocuments, setAnalyzingDocuments] = useState(new Set());
  const [documentAnalyses, setDocumentAnalyses] = useState(new Map());

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

  // Analyze document for summary and tasks
  const handleAnalyze = async (document) => {
    if (!document.content && (!document.file_name || !document.is_processed)) {
      setError('Document needs to have content or be processed before analysis');
      return;
    }

    try {
      setAnalyzingDocuments(prev => new Set([...prev, document.id]));
      setError('');
      
      const analysis = await documentAPI.analyzeDocument(document.id);
      
      // Update the analysis cache
      setDocumentAnalyses(prev => new Map([...prev, [document.id, analysis]]));
      
      // Update the document in the list
      setDocuments(prevDocs => 
        prevDocs.map(doc => 
          doc.id === document.id 
            ? { ...doc, summary: analysis.summary, tasks: analysis.tasks }
            : doc
        )
      );
      
      setSuccess(`✨ Analysis completed! Generated summary and ${analysis.tasks?.length || 0} action items for "${document.title}"`);
    } catch (err) {
      setError('Failed to analyze document: ' + err.message);
    } finally {
      setAnalyzingDocuments(prev => {
        const newSet = new Set(prev);
        newSet.delete(document.id);
        return newSet;
      });
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
    <div className="min-h-screen bg-background dark:bg-slate-900">
      <Header />
    
      <main className="pt-20">
        {/* Hero Section */}
        <section className="py-8 bg-muted/30 dark:bg-slate-800/30">
          <div className="container mx-auto px-6">
            <div className="max-w-4xl mx-auto text-center">
              <Badge className="mb-4 bg-primary text-white px-6 py-2 text-sm font-medium">
                AI Document Management
              </Badge>
              <h1 className="text-4xl md:text-5xl font-display font-bold mb-4 text-foreground dark:text-white">
                Intelligent Document Processing
              </h1>
              <p className="text-lg text-muted-foreground dark:text-slate-300 mb-6 max-w-3xl mx-auto leading-relaxed">
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
                <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 text-red-800 mb-6 shadow-lg animate-in fade-in-50 slide-in-from-top-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center text-white">
                      <span className="text-sm font-bold">!</span>
                    </div>
                    <span className="font-medium">{error}</span>
                  </div>
                </div>
              )}
              {success && (
                <div className="bg-green-50 dark:bg-green-950/20 border-2 border-green-200 dark:border-green-700 rounded-xl p-4 text-green-800 dark:text-green-200 mb-6 shadow-lg animate-in fade-in-50 slide-in-from-top-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center text-white shadow-lg">
                      <CheckCircle2 className="w-4 h-4" />
                    </div>
                    <span className="font-medium">{success}</span>
                  </div>
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
                      <Card key={document.id} className="relative border-2 shadow-lg hover:shadow-xl hover:border-primary/50 transition-all duration-300">
                        {/* Analysis Loading Overlay */}
                        {analyzingDocuments.has(document.id) && (
                          <div className="absolute inset-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm z-10 rounded-lg flex items-center justify-center">
                            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-xl border-2 border-blue-200 dark:border-blue-700 text-center">
                              <div className="w-16 h-16 mx-auto mb-4 bg-blue-600 rounded-full flex items-center justify-center">
                                <Brain className="w-8 h-8 text-white animate-pulse" />
                              </div>
                              <h3 className="text-lg font-semibold text-gray-800 dark:text-gray-100 mb-2">AI Analysis in Progress</h3>
                              <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">Generating summary and extracting tasks...</p>
                              <div className="flex items-center justify-center gap-1">
                                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                                <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-100"></div>
                                <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce delay-200"></div>
                              </div>
                            </div>
                          </div>
                        )}
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
                                onClick={() => handleAnalyze(document)}
                                disabled={analyzingDocuments.has(document.id)}
                                className="group relative overflow-hidden bg-blue-50 dark:bg-blue-950/50 hover:bg-blue-600 hover:text-white border-2 border-blue-200 dark:border-blue-700 hover:border-transparent transition-all duration-300 hover:scale-105 hover:shadow-lg text-blue-800 dark:text-blue-200"
                                title="Generate AI Summary & Extract Tasks"
                              >
                                <div className="flex items-center gap-2">
                                  {analyzingDocuments.has(document.id) ? (
                                    <>
                                      <Loader2 className="w-4 h-4 animate-spin" />
                                      <span className="text-sm font-medium">Analyzing...</span>
                                    </>
                                  ) : (
                                    <>
                                      <Brain className="w-4 h-4 group-hover:animate-bounce" />
                                      <span className="text-sm font-medium">Analyze</span>
                                    </>
                                  )}
                                </div>
                                {/* Sparkle animation overlay */}
                                {!analyzingDocuments.has(document.id) && (
                                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                    <div className="absolute top-1 right-1 w-1 h-1 bg-yellow-300 rounded-full animate-ping"></div>
                                    <div className="absolute bottom-1 left-1 w-1 h-1 bg-blue-300 rounded-full animate-ping delay-150"></div>
                                  </div>
                                )}
                              </Button>
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
                            {/* Analysis Status Banner */}
                            {!document.summary && !document.tasks && !analyzingDocuments.has(document.id) && (
                              <div className="bg-yellow-50 dark:bg-yellow-950/30 border-2 border-dashed border-orange-200 dark:border-orange-700 rounded-xl p-4 text-center">
                                <div className="flex items-center justify-center gap-3 mb-3">
                                  <div className="w-8 h-8 rounded-full bg-orange-500 flex items-center justify-center text-white">
                                    <Brain className="w-4 h-4" />
                                  </div>
                                  <span className="text-orange-800 dark:text-orange-200 font-semibold">Ready for AI Analysis</span>
                                </div>
                                <p className="text-sm text-orange-700 dark:text-orange-300 mb-3">
                                  Click the "Analyze" button to generate an AI summary and extract action items from this document.
                                </p>
                                <Badge className="bg-orange-500 text-white border-0 px-4 py-1 text-xs animate-pulse">
                                  ⚡ Click Analyze to get started
                                </Badge>
                              </div>
                            )}
                            {/* AI Analysis Results */}
                            {(document.summary || document.tasks) && (
                              <div className="bg-blue-50 dark:bg-blue-950/20 border-2 border-blue-200 dark:border-blue-700 rounded-xl p-6 space-y-6 shadow-lg hover:shadow-xl transition-all duration-300 animate-in fade-in-50 slide-in-from-bottom-4">
                                <div className="flex items-center gap-3 text-blue-800 dark:text-blue-200 font-semibold">
                                  <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white shadow-lg">
                                    <Brain className="w-5 h-5" />
                                  </div>
                                  <span className="text-lg">AI Analysis Results</span>
                                  <Badge className="ml-auto bg-green-600 text-white border-0 px-3 py-1 text-xs">
                                    ✨ Complete
                                  </Badge>
                                </div>
                                
                                {/* Summary */}
                                {document.summary && (
                                  <div className="space-y-3">
                                    <div className="flex items-center gap-2">
                                      <div className="w-6 h-6 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                                        <FileText className="w-3 h-3" />
                                      </div>
                                      <h4 className="text-base font-semibold text-blue-900 dark:text-blue-100">Executive Summary</h4>
                                    </div>
                                    <div className="bg-white dark:bg-slate-800 backdrop-blur-sm rounded-lg p-4 border border-blue-200 dark:border-blue-600 shadow-sm hover:shadow-md transition-shadow duration-300">
                                      <p className="text-sm text-blue-800 dark:text-blue-100 leading-relaxed">
                                        {document.summary}
                                      </p>
                                    </div>
                                  </div>
                                )}
                                
                                {/* Tasks */}
                                {document.tasks && document.tasks.length > 0 && (
                                  <div className="space-y-3">
                                    <div className="flex items-center gap-2">
                                      <div className="w-6 h-6 rounded-lg bg-purple-600 flex items-center justify-center text-white">
                                        <CheckCircle2 className="w-3 h-3" />
                                      </div>
                                      <h4 className="text-base font-semibold text-blue-900 dark:text-blue-100">Action Items</h4>
                                      <Badge variant="secondary" className="bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-200 border-purple-200 dark:border-purple-700 px-2 py-1 text-xs">
                                        {document.tasks.length} tasks
                                      </Badge>
                                    </div>
                                    <div className="grid gap-3">
                                      {document.tasks.slice(0, 5).map((task, index) => (
                                        <div key={index} className="group bg-white dark:bg-slate-800 backdrop-blur-sm rounded-lg p-3 border border-blue-200 dark:border-blue-600 shadow-sm hover:shadow-md hover:border-purple-300 dark:hover:border-purple-500 transition-all duration-300 hover:scale-[1.02]">
                                          <div className="flex items-start gap-3">
                                            <div className="w-5 h-5 rounded-full bg-purple-600 flex items-center justify-center text-white mt-0.5 flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                                              <span className="text-xs font-bold">{index + 1}</span>
                                            </div>
                                            <span className="text-sm text-blue-800 dark:text-blue-100 leading-relaxed group-hover:text-purple-800 dark:group-hover:text-purple-200 transition-colors duration-300">{task}</span>
                                          </div>
                                        </div>
                                      ))}
                                      {document.tasks.length > 5 && (
                                        <div className="bg-white dark:bg-slate-800 rounded-lg p-3 border border-dashed border-blue-300 dark:border-blue-600 text-center">
                                          <p className="text-sm text-blue-600 dark:text-blue-300 font-medium">
                                            + {document.tasks.length - 5} more action items
                                          </p>
                                          <p className="text-xs text-blue-500 dark:text-blue-400 mt-1">Click analyze again to view all tasks</p>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                )}
                                
                                {/* Analysis Timestamp */}
                                <div className="flex items-center justify-between pt-3 border-t border-blue-200 dark:border-blue-600">
                                  <div className="flex items-center gap-2 text-xs text-blue-600 dark:text-blue-300">
                                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                                    <span>Analysis completed</span>
                                  </div>
                                  <div className="text-xs text-blue-500 dark:text-blue-400">
                                    {new Date().toLocaleTimeString()}
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Content Preview */}
                            {document.content && (
                              <div className="bg-muted/30 dark:bg-slate-800/50 rounded-lg p-4 border border-border dark:border-slate-700">
                                <p className="text-sm text-muted-foreground dark:text-slate-300 line-clamp-3">
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
                              <div className="flex items-center gap-4 text-sm text-muted-foreground dark:text-slate-400 bg-primary/5 dark:bg-slate-800/50 rounded-lg p-4 border border-primary/10 dark:border-slate-700">
                                <Upload className="w-4 h-4 text-primary" />
                                <span className="font-medium text-foreground dark:text-slate-200">{document.file_name}</span>
                                <span>({formatFileSize(document.file_size)})</span>
                                <span className="ml-auto">{document.file_type}</span>
                              </div>
                            )}

                            {/* Metadata */}
                            <div className="flex justify-between items-center text-sm text-muted-foreground dark:text-slate-400 pt-4 border-t border-border dark:border-slate-700">
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