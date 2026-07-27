import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
let apiKey: string | null = null;

export const setApiKey = (key: string) => {
  apiKey = key;
};

export const ApiClient = {
  ask: async (payload: { question: string; use_rag: boolean; session_id: string; temperature?: number; max_tokens?: number }) => {
    const response = await axios.post(`${API_BASE}/ask`, payload, {
      headers: { 'X-API-Key': apiKey || '' },
    });
    return response.data;
  },
  upload: async (file: File, sessionId: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);
    const response = await axios.post(`${API_BASE}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data', 'X-API-Key': apiKey || '' },
    });
    return response.data;
  },
  startAudit: async (file?: File, text?: string, sessionId?: string) => {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else if (text) {
      formData.append('text', text);
    }
    if (sessionId) formData.append('session_id', sessionId);
    const response = await axios.post(`${API_BASE}/audit`, formData, {
      headers: { 'Content-Type': 'multipart/form-data', 'X-API-Key': apiKey || '' },
    });
    return response.data;
  },
  getAuditStatus: async (jobId: string) => {
    const response = await axios.get(`${API_BASE}/audit/${jobId}/status`, {
      headers: { 'X-API-Key': apiKey || '' },
    });
    return response.data;
  },
  getAuditReport: async (jobId: string) => {
    const response = await axios.get(`${API_BASE}/audit/${jobId}/report`, {
      headers: { 'X-API-Key': apiKey || '' },
      responseType: 'blob',
    });
    return response.data;
  },
  getAuditResult: async (jobId: string) => {
    const response = await axios.get(`${API_BASE}/audit/${jobId}/result`, {
      headers: { 'X-API-Key': apiKey || '' },
    });
    return response.data;
  },
};
