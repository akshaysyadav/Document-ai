import React, { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

export const ResultViewer = ({ document, onBack }) => {
  const [activeTab, setActiveTab] = useState('summary');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reprocessing, setReprocessing] = useState(false);
  const { toast } = useToast();

  const tabs = [
    { id: 'summary', label: 'Summary', icon: '📄' },
    { id: 'chunks', label: 'Chunks', icon: '🧩' },
    { id: 'tasks', label: 'Tasks', icon: '✅' },
  ];

  useEffect(() => {
    if (document) {
      fetchResults();
    }
  }, [document]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await documentAPI.getDocumentResults(document.id);
      setResults(response);
    } catch (error) {
      console.error('Error fetching results:', error);
      toast({
        title: "Error",
        description: "Failed to fetch document results.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReprocess = async () => {
    if (!window.confirm('Are you sure you want to reprocess this document? This will update the summary and tasks.')) {
      return;
    }

    try {
      setReprocessing(true);
      await documentAPI.reprocessDocument(document.id);
      toast({
        title: "Reprocessing started",
        description: "Document is being reprocessed. Results will be updated shortly.",
      });
      
      // Wait a bit and then refresh results
      setTimeout(() => {
        fetchResults();
      }, 2000);
    } catch (error) {
      console.error('Error reprocessing document:', error);
      toast({
        title: "Reprocessing failed",
        description: "Failed to start reprocessing.",
        variant: "destructive",
      });
    } finally {
      setReprocessing(false);
    }
  };

  const handleTaskUpdate = async (taskId, updates) => {
    try {
      await documentAPI.updateTask(taskId, updates);
      toast({
        title: "Task updated",
        description: "Task has been successfully updated.",
      });
      fetchResults(); // Refresh results
    } catch (error) {
      console.error('Error updating task:', error);
      toast({
        title: "Update failed",
        description: "Failed to update task.",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">No results available for this document.</p>
        <button
          onClick={onBack}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Back to Documents
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{results.title}</h2>
          <p className="text-gray-600">Document ID: {results.doc_id}</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={handleReprocess}
            disabled={reprocessing}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {reprocessing ? 'Reprocessing...' : 'Re-run NLP'}
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Back to Documents
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {activeTab === 'summary' && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Summary</h3>
            {results.summary ? (
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed">{results.summary}</p>
              </div>
            ) : (
              <div className="text-center py-8">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">No summary available</p>
                <p className="text-xs text-gray-400">Try reprocessing the document</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'chunks' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Document Chunks</h3>
              <span className="text-sm text-gray-500">{results.chunks?.length || 0} chunks</span>
            </div>
            
            {results.chunks && results.chunks.length > 0 ? (
              <div className="space-y-4">
                {results.chunks.map((chunk, index) => (
                  <ChunkCard key={chunk.id} chunk={chunk} index={index} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8 bg-white border border-gray-200 rounded-lg">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">No chunks available</p>
                <p className="text-xs text-gray-400">Try reprocessing the document</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'tasks' && (
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">Extracted Tasks</h3>
              <span className="text-sm text-gray-500">{results.tasks?.length || 0} tasks</span>
            </div>
            
            {results.tasks && results.tasks.length > 0 ? (
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Task
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Priority
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Assignee
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Due Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.tasks.map((task) => (
                      <TaskRow 
                        key={task.id} 
                        task={task} 
                        onUpdate={handleTaskUpdate}
                      />
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 bg-white border border-gray-200 rounded-lg">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">No tasks extracted</p>
                <p className="text-xs text-gray-400">Try reprocessing the document</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const ChunkCard = ({ chunk, index }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-sm font-medium text-gray-900">Chunk {chunk.chunk_no}</span>
            {chunk.page_no && (
              <span className="text-xs text-gray-500">(Page {chunk.page_no})</span>
            )}
            <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
              chunk.status === 'processed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {chunk.status}
            </span>
          </div>
          
          <p className="text-sm text-gray-700 mb-3">
            {chunk.text_excerpt}
            {chunk.text_excerpt.length === 200 && (
              <span className="text-gray-400">...</span>
            )}
          </p>

          {chunk.summary && (
            <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-medium text-blue-800 mb-1">Summary:</p>
              <p className="text-sm text-blue-700">{chunk.summary}</p>
            </div>
          )}

          {chunk.entities && chunk.entities.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-700 mb-2">Entities:</p>
              <div className="flex flex-wrap gap-2">
                {chunk.entities.map((entity, idx) => (
                  <span key={idx} className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                    {entity.label}: {entity.text}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
        
        <button
          onClick={() => setExpanded(!expanded)}
          className="ml-4 px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
        >
          {expanded ? 'Show Less' : 'Show More'}
        </button>
      </div>
      
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-700">{chunk.text}</p>
        </div>
      )}
    </div>
  );
};

const TaskRow = ({ task, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    assignee: task.assignee || '',
    due_date: task.due_date ? task.due_date.split('T')[0] : '',
    status: task.status,
    priority: task.priority,
  });

  const handleSave = () => {
    onUpdate(task.id, editData);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditData({
      assignee: task.assignee || '',
      due_date: task.due_date ? task.due_date.split('T')[0] : '',
      status: task.status,
      priority: task.priority,
    });
    setIsEditing(false);
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      low: 'bg-green-100 text-green-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-red-100 text-red-800',
    };
    return colors[priority] || 'bg-gray-100 text-gray-800';
  };

  const getStatusBadge = (status) => {
    const colors = {
      open: 'bg-blue-100 text-blue-800',
      'in-progress': 'bg-yellow-100 text-yellow-800',
      done: 'bg-green-100 text-green-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4">
        <div className="text-sm text-gray-900 max-w-xs">
          {task.task_text}
        </div>
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {isEditing ? (
          <select
            value={editData.priority}
            onChange={(e) => setEditData({...editData, priority: e.target.value})}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        ) : (
          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPriorityBadge(task.priority)}`}>
            {task.priority}
          </span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {isEditing ? (
          <select
            value={editData.status}
            onChange={(e) => setEditData({...editData, status: e.target.value})}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          >
            <option value="open">Open</option>
            <option value="in-progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        ) : (
          <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(task.status)}`}>
            {task.status.replace('-', ' ')}
          </span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {isEditing ? (
          <input
            type="text"
            value={editData.assignee}
            onChange={(e) => setEditData({...editData, assignee: e.target.value})}
            placeholder="Assignee"
            className="text-sm border border-gray-300 rounded px-2 py-1 w-24"
          />
        ) : (
          <span className="text-sm text-gray-900">{task.assignee || '-'}</span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap">
        {isEditing ? (
          <input
            type="date"
            value={editData.due_date}
            onChange={(e) => setEditData({...editData, due_date: e.target.value})}
            className="text-sm border border-gray-300 rounded px-2 py-1"
          />
        ) : (
          <span className="text-sm text-gray-900">
            {task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}
          </span>
        )}
      </td>
      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
        {isEditing ? (
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              className="text-green-600 hover:text-green-900"
            >
              Save
            </button>
            <button
              onClick={handleCancel}
              className="text-gray-600 hover:text-gray-900"
            >
              Cancel
            </button>
          </div>
        ) : (
          <button
            onClick={() => setIsEditing(true)}
            className="text-blue-600 hover:text-blue-900"
          >
            Edit
          </button>
        )}
      </td>
    </tr>
  );
};
