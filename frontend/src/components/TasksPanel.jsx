import React, { useState, useEffect } from 'react';
import { documentAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

export const TasksPanel = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTasks, setSelectedTasks] = useState(new Set());
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    assignee: '',
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchAllTasks();
  }, []);

  const fetchAllTasks = async () => {
    try {
      setLoading(true);
      // Get all documents and then fetch tasks for each
      const documents = await documentAPI.getDocuments({ page: 1, size: 100 });
      const allTasks = [];
      
      for (const doc of documents.documents) {
        try {
          const results = await documentAPI.getDocumentResults(doc.id);
          if (results.tasks) {
            allTasks.push(...results.tasks.map(task => ({
              ...task,
              document_title: doc.title,
              document_id: doc.id,
            })));
          }
        } catch (error) {
          console.warn(`Failed to fetch tasks for document ${doc.id}:`, error);
        }
      }
      
      setTasks(allTasks);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      toast({
        title: "Error",
        description: "Failed to fetch tasks.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = tasks.filter(task => {
    if (filters.status && task.status !== filters.status) return false;
    if (filters.priority && task.priority !== filters.priority) return false;
    if (filters.assignee && task.assignee !== filters.assignee) return false;
    return true;
  });

  const handleSelectTask = (taskId) => {
    const newSelected = new Set(selectedTasks);
    if (newSelected.has(taskId)) {
      newSelected.delete(taskId);
    } else {
      newSelected.add(taskId);
    }
    setSelectedTasks(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedTasks.size === filteredTasks.length) {
      setSelectedTasks(new Set());
    } else {
      setSelectedTasks(new Set(filteredTasks.map(task => task.id)));
    }
  };

  const handleBulkAssign = async () => {
    if (selectedTasks.size === 0) return;
    
    const assignee = prompt('Enter assignee name:');
    if (!assignee) return;

    try {
      for (const taskId of selectedTasks) {
        await documentAPI.updateTask(taskId, { assignee });
      }
      
      toast({
        title: "Tasks updated",
        description: `${selectedTasks.size} tasks assigned to ${assignee}.`,
      });
      
      setSelectedTasks(new Set());
      fetchAllTasks();
    } catch (error) {
      console.error('Error updating tasks:', error);
      toast({
        title: "Update failed",
        description: "Failed to update tasks.",
        variant: "destructive",
      });
    }
  };

  const handleBulkStatusUpdate = async (status) => {
    if (selectedTasks.size === 0) return;

    try {
      for (const taskId of selectedTasks) {
        await documentAPI.updateTask(taskId, { status });
      }
      
      toast({
        title: "Tasks updated",
        description: `${selectedTasks.size} tasks marked as ${status}.`,
      });
      
      setSelectedTasks(new Set());
      fetchAllTasks();
    } catch (error) {
      console.error('Error updating tasks:', error);
      toast({
        title: "Update failed",
        description: "Failed to update tasks.",
        variant: "destructive",
      });
    }
  };

  const handleTaskUpdate = async (taskId, updates) => {
    try {
      await documentAPI.updateTask(taskId, updates);
      toast({
        title: "Task updated",
        description: "Task has been successfully updated.",
      });
      fetchAllTasks();
    } catch (error) {
      console.error('Error updating task:', error);
      toast({
        title: "Update failed",
        description: "Failed to update task.",
        variant: "destructive",
      });
    }
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

  const uniqueAssignees = [...new Set(tasks.map(task => task.assignee).filter(Boolean))];
  const statusOptions = ['open', 'in-progress', 'done'];
  const priorityOptions = ['low', 'medium', 'high'];

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Tasks</h2>
          <p className="text-gray-600">Extracted tasks from uploaded documents</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters({...filters, status: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              {statusOptions.map(status => (
                <option key={status} value={status}>
                  {status.replace('-', ' ')}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={filters.priority}
              onChange={(e) => setFilters({...filters, priority: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Priority</option>
              {priorityOptions.map(priority => (
                <option key={priority} value={priority}>
                  {priority}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
            <select
              value={filters.assignee}
              onChange={(e) => setFilters({...filters, assignee: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Assignees</option>
              {uniqueAssignees.map(assignee => (
                <option key={assignee} value={assignee}>
                  {assignee}
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => setFilters({ status: '', priority: '', assignee: '' })}
              className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Tasks Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Task
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Document
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
            {filteredTasks.map((task) => (
              <tr key={task.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-xs">
                    {task.task_text}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {task.document_title}
                  </div>
                  <div className="text-xs text-gray-500">
                    ID: {task.document_id}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPriorityBadge(task.priority)}`}>
                    {task.priority}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(task.status)}`}>
                    {task.status.replace('-', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {task.assignee || '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <TaskQuickActions task={task} onUpdate={handleTaskUpdate} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredTasks.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks found</h3>
            <p className="mt-1 text-sm text-gray-500">
              No tasks have been extracted from documents yet.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

const TaskQuickActions = ({ task, onUpdate }) => {
  const handleQuickAssign = () => {
    const assignee = prompt('Enter assignee name:');
    if (assignee) {
      onUpdate(task.id, { assignee });
    }
  };

  const handleQuickStatus = (status) => {
    onUpdate(task.id, { status });
  };

  return (
    <div className="flex space-x-2">
      <button
        onClick={handleQuickAssign}
        className="text-blue-600 hover:text-blue-900 text-xs"
      >
        Assign
      </button>
      {task.status !== 'done' && (
        <button
          onClick={() => handleQuickStatus('done')}
          className="text-green-600 hover:text-green-900 text-xs"
        >
          Mark Done
        </button>
      )}
    </div>
  );
};

