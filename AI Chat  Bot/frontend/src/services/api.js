import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth-storage');
    if (token) {
      try {
        const parsed = JSON.parse(token);
        if (parsed.state?.token) {
          config.headers.Authorization = `Bearer ${parsed.state.token}`;
        }
      } catch (error) {
        console.error('Error parsing auth storage:', error);
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle authentication errors
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('auth-storage');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Chat API methods
export const chatAPI = {
  sendMessage: (message, conversationId = null) => {
    const formData = new FormData();
    formData.append('message', message);
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }
    return api.post('/chat/send', formData);
  },

  getConversations: (limit = 20) => {
    return api.get('/chat/conversations', { params: { limit } });
  },

  getConversation: (conversationId) => {
    return api.get(`/chat/conversations/${conversationId}`);
  },

  deleteConversation: (conversationId) => {
    return api.delete(`/chat/conversations/${conversationId}`);
  },

  exportConversation: (conversationId, format = 'txt') => {
    return api.get(`/export/conversation/${conversationId}`, {
      params: { format },
      responseType: 'blob',
    });
  },
};

// File API methods
export const fileAPI = {
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getKnowledgeBase: () => {
    return api.get('/files/knowledge-base');
  },

  deleteDocument: (documentId) => {
    return api.delete(`/files/${documentId}`);
  },
};

// Plugin API methods
export const pluginAPI = {
  getPlugins: () => {
    return api.get('/plugins');
  },

  executePlugin: (pluginName, params) => {
    return api.post(`/plugins/${pluginName}/execute`, params);
  },
};

// User API methods
export const userAPI = {
  getProfile: () => {
    return api.get('/users/profile');
  },

  updateProfile: (profileData) => {
    return api.put('/users/profile', profileData);
  },

  changePassword: (passwordData) => {
    const formData = new FormData();
    formData.append('current_password', passwordData.currentPassword);
    formData.append('new_password', passwordData.newPassword);
    return api.put('/users/password', formData);
  },
};

// Health check
export const healthAPI = {
  check: () => {
    return api.get('/health');
  },
};

export default api;
