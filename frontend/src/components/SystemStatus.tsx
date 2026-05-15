import { useEffect, useState } from "react";
import { API_BASE, JAVA_BASE } from "../config";
import "../styles/components.css";

interface ServiceStatus {
  backend: boolean;
  model: boolean;
  java: boolean;
}

export function SystemStatus() {
  const [status, setStatus] = useState<ServiceStatus>({
    backend: false,
    model: false,
    java: false,
  });

  useEffect(() => {
    const checkHealth = async () => {
      let backendOk = false;
      let modelOk = false;
      let javaOk = false;

      try {
        const response = await fetch(`${API_BASE}/health`, { method: "GET" });
        if (response.ok) backendOk = true;
      } catch {
        backendOk = false;
      }

      if (backendOk) {
        try {
          const modelResponse = await fetch(`${API_BASE}/api/credit/model-info`, { method: "GET" });
          if (modelResponse.ok) {
            const data = (await modelResponse.json()) as { is_loaded?: boolean };
            modelOk = Boolean(data.is_loaded);
          }
        } catch {
          modelOk = false;
        }
      }

      try {
        const javaRes = await fetch(`${JAVA_BASE}/api/engine/health`, { method: "GET" });
        javaOk = javaRes.ok;
      } catch {
        javaOk = false;
      }

      setStatus({ backend: backendOk, model: modelOk, java: javaOk });
    };

    void checkHealth();
    const interval = setInterval(() => void checkHealth(), 8000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="status-bar" aria-live="polite">
      <div className="status-item">
        <span className={`status-indicator ${status.backend ? "active" : "inactive"}`} />
        <span>API</span>
      </div>
      <div className="status-item">
        <span className={`status-indicator ${status.model ? "active" : "inactive"}`} />
        <span>Model</span>
      </div>
      <div className="status-item">
        <span className={`status-indicator ${status.java ? "active" : "inactive"}`} />
        <span>Java</span>
      </div>
    </div>
  );
}
