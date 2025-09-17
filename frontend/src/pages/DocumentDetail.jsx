import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { documentAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ArrowLeft, FileText, Download, Calendar, Tag, AlertCircle, CheckCircle2, Clock, XCircle } from 'lucide-react';

const DocumentDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [document, setDocument] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocumentDetails = async () => {
      try {
        setLoading(true);
        
        // Fetch document info and results in parallel
        const [docResponse, resultsResponse] = await Promise.all([
          documentAPI.getDocument(id),
          documentAPI.getDocumentResults(id)
        ]);
        
        console.log('Document response:', docResponse);
        console.log('Results response:', resultsResponse);
        
        setDocument(docResponse);
        setResults(resultsResponse);
      } catch (error) {
        console.error('Error fetching document details:', error);
        
        // Try to fetch results separately if parallel fetch failed
        try {
          const docResponse = await documentAPI.getDocument(id);
          setDocument(docResponse);
          console.log('Document fetched successfully:', docResponse);
          
          const resultsResponse = await documentAPI.getDocumentResults(id);
          setResults(resultsResponse);
          console.log('Results fetched successfully:', resultsResponse);
        } catch (separateError) {
          console.error('Separate fetch also failed:', separateError);
          toast({
            title: "Error",
            description: "Failed to load document details.",
            variant: "destructive",
          });
        }
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchDocumentDetails();
    }
  }, [id, toast]);

  const handleDownload = async () => {
    if (!document?.file_path) {
      toast({
        title: "No file available",
        description: "This document doesn't have an associated file.",
        variant: "destructive",
      });
      return;
    }

    try {
      await documentAPI.downloadFile(document.id, document.file_name);
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
      uploaded: { variant: 'secondary', icon: Clock, label: 'Uploaded' },
      processing: { variant: 'default', icon: Clock, label: 'Processing' },
      processed: { variant: 'default', icon: CheckCircle2, label: 'Processed' },
      failed: { variant: 'destructive', icon: XCircle, label: 'Failed' },
    };

    const config = statusConfig[status] || { variant: 'secondary', icon: AlertCircle, label: status };
    const Icon = config.icon;
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    );
  };

  const getPriorityBadge = (priority) => {
    const priorityConfig = {
      high: { variant: 'destructive', label: 'High' },
      medium: { variant: 'default', label: 'Medium' },
      low: { variant: 'secondary', label: 'Low' },
    };

    const config = priorityConfig[priority] || { variant: 'secondary', label: priority };
    
    return (
      <Badge variant={config.variant} className="text-xs">
        {config.label}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '';
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-6">
            <Skeleton className="h-10 w-48" />
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                <Card>
                  <CardHeader>
                    <Skeleton className="h-6 w-32" />
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <Skeleton className="h-6 w-24" />
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="space-y-2">
                        <Skeleton className="h-4 w-full" />
                        <Skeleton className="h-4 w-2/3" />
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <Skeleton className="h-6 w-32" />
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
            <CardTitle>Document Not Found</CardTitle>
            <CardDescription>
              The document you're looking for doesn't exist or has been removed.
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button onClick={() => navigate('/dashboard')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{document.title}</h1>
              <p className="text-gray-500 mt-1">
                Uploaded {formatDate(document.created_at)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {getStatusBadge(document.status)}
            {document.file_path && (
              <Button onClick={handleDownload} className="flex items-center gap-2">
                <Download className="h-4 w-4" />
                Download File
              </Button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Document Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Document Summary
                </CardTitle>
                <CardDescription>
                  AI-generated summary of the document content
                </CardDescription>
              </CardHeader>
              <CardContent>
                {results?.chunks && results.chunks.length > 0 ? (
                  <div className="prose prose-sm max-w-none">
                    <div className="text-gray-700 leading-relaxed space-y-4">
                      {results.chunks.map((chunk, index) => (
                        chunk.summary && (
                          <div key={index} className="border-l-2 border-blue-200 pl-4">
                            <div className="text-sm font-medium text-blue-600 mb-1">
                              Section {index + 1}
                            </div>
                            <p className="whitespace-pre-wrap text-gray-700">
                              {chunk.summary}
                            </p>
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                ) : results?.summary ? (
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {results.summary}
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Summary Available</h3>
                    <p className="text-gray-500">
                      {document.status === 'processing' 
                        ? 'Document is still being processed. Summary will appear once processing is complete.'
                        : 'Summary could not be generated for this document.'
                      }
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Extracted Tasks */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5" />
                  Extracted Tasks
                </CardTitle>
                <CardDescription>
                  Action items and tasks identified in the document
                </CardDescription>
              </CardHeader>
              <CardContent>
                {results?.tasks && results.tasks.length > 0 ? (
                  <ScrollArea className="h-96">
                    <div className="space-y-4">
                      {results.tasks
                        .filter(task => task.id !== "no-tasks") // Filter out placeholder tasks
                        .map((task, index) => (
                        <Card key={task.id || index} className="border-l-4 border-l-blue-500">
                          <CardContent className="pt-4">
                            <div className="flex items-start justify-between mb-2">
                              <p className="text-sm font-medium text-gray-900 flex-1">
                                {task.task_text}
                              </p>
                              {task.priority && getPriorityBadge(task.priority)}
                            </div>
                            <div className="flex items-center space-x-2 text-xs text-gray-500">
                              <Badge variant="outline" className="text-xs">
                                {task.status || 'open'}
                              </Badge>
                              {task.due_date && (
                                <span className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  {formatDate(task.due_date)}
                                </span>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                      {/* Show message if only "no-tasks" entries exist */}
                      {results.tasks.every(task => task.id === "no-tasks") && (
                        <div className="text-center py-4">
                          <CheckCircle2 className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                          <p className="text-sm text-gray-500">
                            {results.tasks[0]?.task_text || "No actionable tasks found in this document."}
                          </p>
                        </div>
                      )}
                    </div>
                  </ScrollArea>
                ) : (
                  <div className="text-center py-8">
                    <CheckCircle2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Tasks Found</h3>
                    <p className="text-gray-500">
                      {document.status === 'processing' 
                        ? 'Document is still being processed. Tasks will appear once processing is complete.'
                        : 'No actionable tasks were identified in this document.'
                      }
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Document Info */}
            <Card>
              <CardHeader>
                <CardTitle>Document Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">File Name</label>
                  <p className="text-sm text-gray-900">{document.file_name || 'N/A'}</p>
                </div>
                
                {document.file_size && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">File Size</label>
                    <p className="text-sm text-gray-900">{formatFileSize(document.file_size)}</p>
                  </div>
                )}
                
                {document.description && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Description</label>
                    <p className="text-sm text-gray-900">{document.description}</p>
                  </div>
                )}
                
                {document.tags && document.tags.length > 0 && (
                  <div>
                    <label className="text-sm font-medium text-gray-500 mb-2 block">Tags</label>
                    <div className="flex flex-wrap gap-1">
                      {document.tags.map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <div className="mt-1">
                    {getStatusBadge(document.status)}
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-500">Created</label>
                  <p className="text-sm text-gray-900">{formatDate(document.created_at)}</p>
                </div>
                
                {document.processed_at && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Processed</label>
                    <p className="text-sm text-gray-900">{formatDate(document.processed_at)}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Processing Stats */}
            {results && (
              <Card>
                <CardHeader>
                  <CardTitle>Processing Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Text Chunks</span>
                    <Badge variant="outline">{results.chunks?.length || 0}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Entities Found</span>
                    <Badge variant="outline">{results.entities?.length || 0}</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Tasks Extracted</span>
                    <Badge variant="outline">{results.tasks?.length || 0}</Badge>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentDetail; 