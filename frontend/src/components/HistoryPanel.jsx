import React from 'react';
import { FiMessageSquare } from 'react-icons/fi';
import './HistoryPanel.css';

export default function HistoryPanel() {
  const mockHistory = [
    "Aviation Data Stats",
    "Recent Flights Overview",
    "JFK Airport Weather",
    "AA100 Radar Tracks"
  ];

  return (
    <div className="history-panel">
      <div className="history-label">Recent Queries</div>
      <div className="history-list">
        {mockHistory.map((title, i) => (
          <button key={i} className="history-item">
            <FiMessageSquare className="history-icon" />
            <span className="history-text">{title}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
