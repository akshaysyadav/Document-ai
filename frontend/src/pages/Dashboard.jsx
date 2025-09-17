import React, { useState } from 'react';
import { UploadPanel } from '../components/UploadPanel';
import { DocumentList } from '../components/DocumentList';
import { ResultViewer } from '../components/ResultViewer';
import { TasksPanel } from '../components/TasksPanel';

const Dashboard = () => {
  const [activeView, setActiveView] = useState('upload');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleDocumentUploaded = () => {
    setRefreshTrigger(prev => prev + 1);
    setActiveView('documents');
  };

  const handleViewResults = (document) => {
    setSelectedDocument(document);
    setActiveView('results');
  };

  const sidebarItems = [
    { id: 'upload', label: 'Upload', icon: '📤' },
    { id: 'documents', label: 'Documents', icon: '📄' },
    { id: 'results', label: 'Results', icon: '📊' },
    { id: 'tasks', label: 'Tasks', icon: '✅' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  const renderActiveView = () => {
    switch (activeView) {
      case 'upload':
        return <UploadPanel onDocumentUploaded={handleDocumentUploaded} />;
      case 'documents':
        return (
          <DocumentList 
            onViewResults={handleViewResults}
            refreshTrigger={refreshTrigger}
          />
        );
      case 'results':
        return selectedDocument ? (
          <ResultViewer 
            document={selectedDocument}
            onBack={() => setActiveView('documents')}
          />
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500">No document selected</p>
            <button 
              onClick={() => setActiveView('documents')}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Back to Documents
            </button>
          </div>
        );
      case 'tasks':
        return <TasksPanel />;
      case 'settings':
        return (
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">Settings</h2>
            <div className="bg-white rounded-2xl shadow-sm p-6">
              <p className="text-gray-600">Settings panel coming soon...</p>
            </div>
          </div>
        );
      default:
        return <UploadPanel onDocumentUploaded={handleDocumentUploaded} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-lg">
          <div className="p-6">
            <h1 className="text-2xl font-bold text-gray-800 mb-8">
              KMRL Dashboard
            </h1>
            <nav className="space-y-2">
              {sidebarItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  className={`w-full flex items-center px-4 py-3 text-left rounded-lg transition-colors ${
                    activeView === item.id
                      ? 'bg-blue-50 text-blue-600 border-r-2 border-blue-600'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-xl mr-3">{item.icon}</span>
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-3xl font-bold text-gray-800 capitalize">
                {activeView === 'results' ? 'Document Results' : activeView}
              </h2>
              <p className="text-gray-600 mt-1">
                {activeView === 'upload' && 'Upload and process documents'}
                {activeView === 'documents' && 'Manage your documents'}
                {activeView === 'results' && 'View document analysis results'}
                {activeView === 'tasks' && 'Manage extracted tasks'}
                {activeView === 'settings' && 'Configure system settings'}
              </p>
            </div>
            
            <div className="bg-white rounded-2xl shadow-sm min-h-[600px]">
              {renderActiveView()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;