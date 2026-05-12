import React from 'react';
import './ChatArea.css';
import { FiUser, FiCpu } from 'react-icons/fi';

export default function ChatArea({ messages }) {
  return (
    <div className="chat-area">
      {messages.length === 0 ? (
        <div className="empty-state">
          <h2>SkyQuery</h2>
          <p>Ask a question about your Trino data.</p>
        </div>
      ) : (
        <div className="messages-list">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-row ${msg.role}`}>
              <div className="message-content-wrapper">
                <div className="avatar">
                  {msg.role === 'user' ? <FiUser /> : <FiCpu />}
                </div>
                <div className="message-bubble">
                  {msg.content}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
