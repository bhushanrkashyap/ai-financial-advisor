import { useEffect, useState } from 'react';
import '../styles/components.css';

interface ServiceStatus {
  backend: boolean;
  model: boolean;
  java: boolean;
}

export function SystemStatus() {
  const [status, setStatus] = useState<ServiceStatus>({
    backend: false,
    model: false,
    java: true, // Java runs separately
  });

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health', { method: 'GET' });
        if (response.ok) {
          setStatus(prev => ({ ...prev, backend: true }));

          // Check model info
          try {
            const modelResponse = await fetch('http://localhost:8000/api/credit/model-info', {
              method: 'GET',
            });
            if (modelResponse.ok) {
              setStatus(prev => ({ ...prev, model: true }));
            }
          } catch {
            setStatus(prev => ({ ...prev, model: false }));
          }
        }
      } catch {
        setStatus(prev => ({ ...prev, backend: false, model: false }));
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-bar">
      <div className="status-item">
        <span className={`status-indicator ${status.backend ? 'active' : 'inactive'}`}></span>
        <span>Backend API</span>
      </div>
      <div className="status-item">
        <span className={`status-indicator ${status.model ? 'active' : 'inactive'}`}></span>
        <span>ML Model</span>
      </div>
      <div className="status-item">
        <span className={`status-indicator ${status.java ? 'active' : 'inactive'}`}></span>
        <span>Java Engine</span>
      </div>
      <div className="status-item">
        <span className={`status-indicator ${status.backend ? 'active' : 'inactive'}`}></span>
        <span>System Ready</span>
      </div>
    </div>
  );
}
