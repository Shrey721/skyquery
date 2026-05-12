import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import ChatInput from './components/ChatInput';
import ConnectionPanel from './components/ConnectionPanel';
import Login from './components/Login';
import { apiClient } from './services/apiClient';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [showConnectionPanel, setShowConnectionPanel] = useState(false);
  const [activeConnection, setActiveConnection] = useState(null);
  const [schema, setSchema] = useState(null);
  const [isLoadingConnection, setIsLoadingConnection] = useState(true);
  const [user, setUser] = useState(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    setIsCheckingAuth(true);
    try {
      const currentUser = await apiClient.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
        // Only check connection if authenticated
        checkExistingConnection();
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setIsCheckingAuth(false);
    }
  };

  const checkExistingConnection = async () => {
    setIsLoadingConnection(true);
    try {
      const conn = await apiClient.getActiveConnection();
      if (conn) {
        setActiveConnection(conn);
        // Only load schema if there IS an active connection
        await loadSchema();
      } else {
        // No active connection — don't show any metadata
        setActiveConnection(null);
        setSchema(null);
        // Automatically prompt for connection if none exists
        setShowConnectionPanel(true);
      }
    } catch (e) {
      // Backend unreachable or error — don't show stale data
      console.error('Failed to check active connection:', e);
      setActiveConnection(null);
      setSchema(null);
    } finally {
      setIsLoadingConnection(false);
    }
  };

  const loadSchema = async () => {
    try {
      const meta = await apiClient.getMetadataSchema();
      if (meta) {
        setSchema(meta);
      } else {
        setSchema(null);
      }
    } catch (e) {
      console.error('Failed to load schema:', e);
      setSchema(null);
    }
  };

  /**
   * Called from ConnectionPanel after a successful /connect call.
   * Receives { connection, metadata } from the combined endpoint.
   */
  const handleConnect = ({ connection, metadata }) => {
    setActiveConnection(connection);
    if (metadata) {
      setSchema(metadata);
    }
  };

  /**
   * Disconnect: deactivate connection, clear metadata.
   */
  const handleDisconnect = async () => {
    try {
      await apiClient.disconnect();
    } catch (e) {
      console.error('Disconnect failed:', e);
    }
    setActiveConnection(null);
    setSchema(null);
  };

  const handleSendMessage = (text) => {
    // 1. Add user message
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);

    // 2. Mock Assistant response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `I'm a mock assistant! You asked: "${text}".\n\nI will soon connect to your Trino backend to query this data for you.` }
      ]);
    }, 1000);
  };

  const handleRefreshMetadata = async () => {
    if (!activeConnection) return;
    try {
      await apiClient.discoverMetadata();
      await loadSchema();
    } catch (e) {
      console.error('Metadata refresh failed:', e);
    }
  };

  if (isCheckingAuth) {
    return <div className="app-loading">Loading...</div>;
  }

  if (!user) {
    return <Login />;
  }

  return (
    <div className="app-container">
      <Sidebar 
        schema={schema} 
        activeConnection={activeConnection}
        isLoading={isLoadingConnection}
        user={user}
        onOpenSettings={() => setShowConnectionPanel(true)} 
        onRefreshMetadata={handleRefreshMetadata}
        onDisconnect={handleDisconnect}
        onLogout={async () => {
          await apiClient.logout();
          setUser(null);
        }}
      />
      
      <main className="main-content">
        <ChatArea messages={messages} />
        <ChatInput onSendMessage={handleSendMessage} />
      </main>

      {showConnectionPanel && (
        <ConnectionPanel 
          onClose={() => setShowConnectionPanel(false)} 
          onConnect={handleConnect}
        />
      )}
    </div>
  );
}

export default App;
