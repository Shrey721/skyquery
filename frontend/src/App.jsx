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
  const [recentQueries, setRecentQueries] = useState([]);
  const [showConnectionPanel, setShowConnectionPanel] = useState(false);
  const [activeConnection, setActiveConnection] = useState(null);
  const [schema, setSchema] = useState(null);
  const [isLoadingConnection, setIsLoadingConnection] = useState(true);
  const [user, setUser] = useState({ id: 'demo-user', username: 'demo-user', avatar_url: 'https://github.com/github.png' });
  const [isCheckingAuth, setIsCheckingAuth] = useState(false);

  useEffect(() => {
    // Demo mode: skip auth and metadata loading, use mock data
    setIsCheckingAuth(false);
    setIsLoadingConnection(false);

    // Provide an initial mock connection and schema for demo visual
    setActiveConnection({ id: 'demo-conn', host: 'demo-cluster' });
    setSchema({
      "aviation.public.flight_ops": {
        columns: ["delayed_flights", "flight_id", "airline", "origin", "destination", "status"],
        description: "Mock table for flight operations"
      },
      "aviation.public.airlines": {
        columns: ["airline_id", "airline_name", "country"],
        description: "Mock table for airlines"
      }
    });
  }, []);

  const handleConnect = ({ connection, metadata }) => {
    // Mock connect behavior
    setActiveConnection({ id: 'demo-conn', host: 'demo-cluster' });
    setShowConnectionPanel(false);
  };

  const handleDisconnect = async () => {
    // Mock disconnect behavior
    setActiveConnection(null);
    setSchema(null);
  };

  const handleSendMessage = async (text) => {
    // 1. Add user message
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);

    // 2. Add loading state
    const loadingMessageIdx = newMessages.length;
    setMessages((prev) => [
      ...prev,
      { role: 'assistant', isLoading: true }
    ]);

    try {
      // Demo Mode: Mock API query delay and response
      await new Promise(r => setTimeout(r, 1500));
      
      const response = {
        summary: "This is a mock UI demo response. Here is the data based on your query.",
        sql: "SELECT * FROM aviation.public.flight_ops\nLIMIT 10;",
        validation: { valid: true },
        selected_tables: ["aviation.public.flight_ops"],
        execution: {
          rows: [
            { id: 1, flight_no: "AA123", status: "Delayed", origin: "JFK", dest: "LAX" },
            { id: 2, flight_no: "DL456", status: "On Time", origin: "ATL", dest: "ORD" },
            { id: 3, flight_no: "UA789", status: "Delayed", origin: "SFO", dest: "EWR" },
            { id: 4, flight_no: "SW321", status: "On Time", origin: "DAL", dest: "HOU" }
          ],
          preview: [
            { id: 1, flight_no: "AA123", status: "Delayed", origin: "JFK", dest: "LAX" },
            { id: 2, flight_no: "DL456", status: "On Time", origin: "ATL", dest: "ORD" }
          ]
        }
      };
      
      setMessages((prev) => {
        const updated = [...prev];
        updated[loadingMessageIdx] = { 
          role: 'assistant', 
          content: response.summary,
          sql: response.sql,
          validation: response.validation,
          selected_tables: response.selected_tables,
          execution: response.execution,
          isError: false
        };
        return updated;
      });

      setRecentQueries(prev => {
        const title = text.length > 30 ? text.substring(0, 30) + '...' : text;
        return [title, ...prev].slice(0, 10);
      });

    } catch (e) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[loadingMessageIdx] = { 
          role: 'assistant', 
          content: `Error: ${e.message}`,
          isError: true
        };
        return updated;
      });
    }
  };

  const handleRefreshMetadata = async () => {
    if (!activeConnection) return;
    // Mock refresh delay
    await new Promise(r => setTimeout(r, 500));
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
        recentQueries={recentQueries}
        isLoading={isLoadingConnection}
        user={user}
        onOpenSettings={() => setShowConnectionPanel(true)} 
        onRefreshMetadata={handleRefreshMetadata}
        onDisconnect={handleDisconnect}
        onLogout={async () => {
          // Mock logout
          setUser(null);
        }}
      />
      
      <main className="main-content">
        <div className="top-navbar">
          <div className="live-badge">
            <span className="live-dot"></span> Live Trino Execution
          </div>
        </div>
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
