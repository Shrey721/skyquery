import React, { useState } from 'react';
import { FiX, FiCheck, FiAlertCircle, FiLoader, FiServer, FiDatabase, FiGrid, FiLayers } from 'react-icons/fi';
import { apiClient } from '../services/apiClient';
import './ConnectionPanel.css';

const STEP_ICONS = {
  'Trino Reachability': FiServer,
  'Catalog Validation': FiDatabase,
  'Schema Validation': FiLayers,
  'Metadata Query': FiGrid,
};

function ValidationStep({ step }) {
  const Icon = STEP_ICONS[step.step] || FiCheck;
  return (
    <div className={`validation-step ${step.passed ? 'passed' : 'failed'}`}>
      <div className="step-icon-wrap">
        {step.passed ? <FiCheck /> : <FiAlertCircle />}
      </div>
      <div className="step-info">
        <span className="step-name">{step.step}</span>
        <span className="step-detail">{step.detail}</span>
      </div>
    </div>
  );
}

export default function ConnectionPanel({ onClose, onConnect }) {
  const [formData, setFormData] = useState({
    host: 'localhost',
    port: 8080,
    catalog: 'aviation',
    schema_name: 'public',
    username: 'trino',
    password: '',
    ssl_enabled: false
  });
  
  const [status, setStatus] = useState('');
  const [statusType, setStatusType] = useState(''); // 'success' | 'error' | 'loading'
  const [validationSteps, setValidationSteps] = useState([]);
  const [testPassed, setTestPassed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (name === 'port' ? parseInt(value) || 0 : value)
    }));
    // Reset validation if details change
    setTestPassed(false);
    setValidationSteps([]);
    setStatus('');
    setStatusType('');
  };

  const handleTest = async () => {
    setIsLoading(true);
    setStatus('Validating connection...');
    setStatusType('loading');
    setTestPassed(false);
    setValidationSteps([]);
    
    try {
      // Mock API delay
      await new Promise(r => setTimeout(r, 1000));
      
      const res = {
        message: 'All checks passed (Mock)',
        steps: [
          { step: 'Trino Reachability', passed: true, detail: 'Mock Reachable' },
          { step: 'Catalog Validation', passed: true, detail: 'Mock Validated' },
          { step: 'Schema Validation', passed: true, detail: 'Mock Schema' },
          { step: 'Metadata Query', passed: true, detail: 'Mock OK' }
        ]
      };
      setValidationSteps(res.steps || []);
      setStatus(res.message || 'All checks passed');
      setStatusType('success');
      setTestPassed(true);
    } catch (e) {
      setValidationSteps(e.steps || []);
      setStatus(e.message || 'Connection test failed');
      setStatusType('error');
      setTestPassed(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConnect = async () => {
    setIsLoading(true);
    setStatus('Connecting and discovering metadata...');
    setStatusType('loading');
    
    try {
      // Mock API delay
      await new Promise(r => setTimeout(r, 1000));

      const res = {
        message: 'Connected successfully (Mock)',
        steps: [
          { step: 'Trino Reachability', passed: true, detail: 'Mock Reachable' },
          { step: 'Catalog Validation', passed: true, detail: 'Mock Validated' },
          { step: 'Schema Validation', passed: true, detail: 'Mock Schema' },
          { step: 'Metadata Query', passed: true, detail: 'Mock OK' }
        ],
        connection: { id: 'demo-conn', host: formData.host },
        metadata: {
          "aviation.public.flight_ops": {
            columns: ["delayed_flights", "flight_id", "airline", "origin", "destination", "status"],
            description: "Mock table for flight operations"
          },
          "aviation.public.airlines": {
            columns: ["airline_id", "airline_name", "country"],
            description: "Mock table for airlines"
          }
        }
      };

      setValidationSteps(res.steps || []);
      setStatus(res.message || 'Connected successfully');
      setStatusType('success');
      
      // Notify parent with both connection and metadata
      setTimeout(() => {
        onConnect({
          connection: res.connection,
          metadata: res.metadata,
        });
        onClose();
      }, 800);
    } catch (e) {
      setValidationSteps(e.steps || []);
      setStatus(e.message || 'Connection failed');
      setStatusType('error');
      setTestPassed(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content connection-panel" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            <FiServer className="header-icon" />
            Trino Connection
          </h2>
          <button className="close-btn" onClick={onClose}><FiX /></button>
        </div>
        
        <div className="modal-body">
          <div className="form-row">
            <div className="form-group flex-3">
              <label>Host</label>
              <input type="text" name="host" value={formData.host} onChange={handleChange} placeholder="e.g. localhost" />
            </div>
            <div className="form-group flex-1">
              <label>Port</label>
              <input type="number" name="port" value={formData.port} onChange={handleChange} />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>Catalog</label>
              <input type="text" name="catalog" value={formData.catalog} onChange={handleChange} placeholder="e.g. aviation" />
            </div>
            <div className="form-group flex-1">
              <label>Schema</label>
              <input type="text" name="schema_name" value={formData.schema_name} onChange={handleChange} placeholder="e.g. public" />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group flex-1">
              <label>Username</label>
              <input type="text" name="username" value={formData.username} onChange={handleChange} />
            </div>
            <div className="form-group flex-1">
              <label>Password <span className="optional-tag">optional</span></label>
              <input type="password" name="password" value={formData.password} onChange={handleChange} />
            </div>
          </div>

          <div className="form-group-checkbox">
            <input type="checkbox" id="ssl_enabled" name="ssl_enabled" checked={formData.ssl_enabled} onChange={handleChange} />
            <label htmlFor="ssl_enabled">Use SSL / TLS</label>
          </div>

          {/* Validation Steps */}
          {validationSteps.length > 0 && (
            <div className="validation-steps-container">
              <div className="validation-steps-label">Validation Results</div>
              {validationSteps.map((step, idx) => (
                <ValidationStep key={idx} step={step} />
              ))}
            </div>
          )}

          {/* Status Message */}
          {status && (
            <div className={`status-message ${statusType}`}>
              {statusType === 'loading' && <FiLoader className="spin-icon" />}
              {statusType === 'success' && <FiCheck />}
              {statusType === 'error' && <FiAlertCircle />}
              <span>{status}</span>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={handleTest} disabled={isLoading}>
            {isLoading && statusType === 'loading' && !testPassed ? 'Validating...' : 'Test Connection'}
          </button>
          <button
            className="btn-primary"
            onClick={handleConnect}
            disabled={isLoading}
          >
            {isLoading && statusType === 'loading' && testPassed ? 'Connecting...' : 'Connect & Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
