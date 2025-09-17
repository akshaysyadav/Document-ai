import React, { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { FileText, Download, Trash2, Search, Calendar, Tag } from 'lucide-react';

export const DocumentList = ({ onViewResults, refreshTrigger }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { toast } = useToast();

  const itemsPerPage = 12;

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await documentAPI.getDocuments({
        page: currentPage,
        size: itemsPerPage,
        search: searchTerm || undefined,
      });
      
      // Sort documents by created_at descending (newest first)
      const sortedDocuments = (response.documents || []).sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
      
      setDocuments(sortedDocuments);
      setTotalPages(response.pages || 1);
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast({
        title: "Error",
        description: "Failed to fetch documents.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [currentPage, searchTerm, refreshTrigger]);

  // Poll for status updates on processing documents
  useEffect(() => {
    const processingDocs = documents.filter(doc => 
      doc.status === 'uploaded' || doc.status === 'processing'
    );
    
    if (processingDocs.length > 0) {
      const interval = setInterval(() => {
        fetchDocuments();
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [documents]);

  const handleDeleteDocument = async (docId, e) => {
    e.stopPropagation(); // Prevent card click
    
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await documentAPI.deleteDocument(docId);
      toast({
        title: "Document deleted",
        description: "Document has been successfully deleted.",
      });
      fetchDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      toast({
        title: "Delete failed",
        description: "Failed to delete document.",
        variant: "destructive",
      });
    }
  };

  const handleDownloadDocument = async (doc, e) => {
    e.stopPropagation(); // Prevent card click
    
    if (!doc.file_path) {
      toast({
        title: "No file available",
        description: "This document doesn't have an associated file.",
        variant: "destructive",
      });
      return;
    }

    try {
      await documentAPI.downloadFile(doc.id, doc.file_name);
      toast({
        title: "Download started",
        description: "File download has been initiated.",
      });
    } catch (error) {
      console.error('Error downloading document:', error);
      toast({
        title: "Download failed",
        description: "Failed to download file.",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      uploaded: { variant: 'secondary', label: 'Uploaded' },
      processing: { variant: 'default', label: 'Processing' },
      processed: { variant: 'default', label: 'Processed' },
      failed: { variant: 'destructive', label: 'Failed' },
    };

    const config = statusConfig[status] || { variant: 'secondary', label: status };
    
    return (
      <Badge variant={config.variant} className="text-xs">
        {config.label}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  if (loading && documents.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Skeleton className="h-10 flex-1" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-3 w-full mb-2" />
                <Skeleton className="h-3 w-2/3" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="flex items-center space-x-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Documents Grid */}
      {documents.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No documents found</h3>
          <p className="text-gray-500">
            {searchTerm ? 'Try adjusting your search terms.' : 'Get started by uploading your first document.'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {documents.map((doc) => (
            <Card 
              key={doc.id} 
              className="cursor-pointer hover:shadow-md transition-shadow duration-200"
              onClick={() => onViewResults(doc)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2 min-w-0 flex-1">
                    <FileText className="h-4 w-4 text-blue-600 flex-shrink-0" />
                    <CardTitle className="text-sm font-medium truncate">
                      {doc.title}
                    </CardTitle>
                  </div>
                  {getStatusBadge(doc.status)}
                </div>
                
                <div className="flex items-center text-xs text-gray-500 space-x-4">
                  <div className="flex items-center space-x-1">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(doc.created_at)}</span>
                  </div>
                  {doc.file_size && (
                    <span>{formatFileSize(doc.file_size)}</span>
                  )}
                </div>
              </CardHeader>
              
              <CardContent className="pt-0">
                {doc.description && (
                  <CardDescription className="text-xs mb-3 line-clamp-2">
                    {doc.description}
                  </CardDescription>
                )}
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1 min-w-0 flex-1">
                    {doc.tags && doc.tags.length > 0 && (
                      <div className="flex items-center space-x-1">
                        <Tag className="h-3 w-3 text-gray-400" />
                        <div className="flex flex-wrap gap-1">
                          {doc.tags.slice(0, 2).map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs px-1 py-0">
                              {tag}
                            </Badge>
                          ))}
                          {doc.tags.length > 2 && (
                            <span className="text-xs text-gray-500">+{doc.tags.length - 2}</span>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    {doc.file_path && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => handleDownloadDocument(doc, e)}
                        className="h-6 w-6 p-0"
                      >
                        <Download className="h-3 w-3" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => handleDeleteDocument(doc.id, e)}
                      className="h-6 w-6 p-0 text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-4">
          <div className="text-sm text-gray-700">
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};
