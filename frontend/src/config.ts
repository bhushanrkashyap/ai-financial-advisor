/** API origins for the browser (override with Vite env in production). */
export const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const JAVA_BASE = import.meta.env.VITE_JAVA_URL ?? "http://localhost:8081";
