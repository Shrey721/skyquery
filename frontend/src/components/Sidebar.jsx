import React, { useState } from 'react';
import { FiMessageSquare, FiPlus, FiSettings, FiDatabase, FiChevronRight, FiChevronDown, FiList, FiRefreshCw, FiZapOff } from 'react-icons/fi';
import './Sidebar.css';
import HistoryPanel from './HistoryPanel';

export default function Sidebar({ schema, activeConnection, recentQueries, isLoading, user, onOpenSettings, onRefreshMetadata, onDisconnect, onLogout }) {
  const [expandedTables, setExpandedTables] = useState({});

  const toggleTable = (tableName) => {
    setExpandedTables(prev => ({
      ...prev,
      [tableName]: !prev[tableName]
    }));
  };

  const hasSchema = schema && schema.tables && schema.tables.length > 0;

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <button className="new-chat-btn">
          <FiPlus className="icon" />
          <span>New query</span>
        </button>
      </div>

      <div className="sidebar-content">
        <HistoryPanel history={recentQueries} />

        {/* Schema section: only shown when connected with valid metadata */}
        {activeConnection && hasSchema && (
          <div className="schema-panel">
            <div className="schema-label-container">
              <div className="schema-label">Database Schema</div>
              <button className="refresh-btn" onClick={onRefreshMetadata} title="Refresh Metadata">
                <FiRefreshCw />
              </button>
            </div>
            <div className="schema-catalog">
              <FiDatabase className="schema-icon" /> 
              {schema.tables[0].catalog}.{schema.tables[0].schema_name}
            </div>
            <div className="schema-list">
              {schema.tables.map(table => (
                <div key={table.table_name} className="schema-table-item">
                  <div 
                    className="schema-table-header" 
                    onClick={() => toggleTable(table.table_name)}
                  >
                    {expandedTables[table.table_name] ? <FiChevronDown /> : <FiChevronRight />}
                    <span>{table.table_name}</span>
                    {table.row_count != null && (
                      <span className="table-row-count">{table.row_count.toLocaleString()} rows</span>
                    )}
                  </div>
                  {expandedTables[table.table_name] && (
                    <div className="schema-columns-list">
                      {table.columns.map(col => (
                        <div key={col.name} className="schema-column-item">
                          <FiList className="column-icon" />
                          <span className="column-name">{col.name}</span>
                          <span className="column-type">{col.data_type}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No connection placeholder */}
        {!activeConnection && !isLoading && (
          <div className="no-connection-placeholder">
            <FiDatabase className="placeholder-icon" />
            <p className="placeholder-title">No database connected</p>
            <p className="placeholder-subtitle">Configure a Trino connection to explore your schema.</p>
            <button className="btn-connect-prompt" onClick={onOpenSettings}>
              Connect to Database
            </button>
          </div>
        )}

        {/* Connected but no tables found */}
        {activeConnection && !hasSchema && !isLoading && (
          <div className="no-connection-placeholder">
            <FiDatabase className="placeholder-icon" />
            <p className="placeholder-title">No tables found</p>
            <p className="placeholder-subtitle">The schema appears empty. Try refreshing or check connection settings.</p>
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        {user && (
          <div className="user-profile">
            <img src={user.avatar_url || 'https://github.com/identicons/default.png'} alt={user.username} className="user-avatar" />
            <div className="user-info-text">
              <span className="user-name">{user.username}</span>
            </div>
            <button className="logout-btn" onClick={onLogout} title="Logout">
              Logout
            </button>
          </div>
        )}
        <div className="connection-status">
          <div className={`status-indicator ${activeConnection ? 'connected' : 'disconnected'}`}></div>
          <span>{activeConnection ? `Connected` : 'Not Connected'}</span>
          {activeConnection && (
            <button className="disconnect-btn" onClick={onDisconnect} title="Disconnect">
              <FiZapOff />
            </button>
          )}
        </div>
        <button className="settings-btn" onClick={onOpenSettings}>
          <FiSettings className="icon" />
          <span>Connection Settings</span>
        </button>
      </div>
    </div>
  );
}
