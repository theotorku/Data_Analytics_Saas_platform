import axios from 'axios';
import toast from 'react-hot-toast';

// API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/v1/auth/refresh`, {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token: newRefreshToken } = response.data;
          localStorage.setItem('token', access_token);
          localStorage.setItem('refreshToken', newRefreshToken);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle other errors
    const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
    
    // Don't show toast for certain endpoints
    const silentEndpoints = ['/auth/me'];
    const shouldShowToast = !silentEndpoints.some(endpoint => 
      originalRequest.url?.includes(endpoint)
    );

    if (shouldShowToast && error.response?.status !== 401) {
      toast.error(errorMessage);
    }

    return Promise.reject(error);
  }
);

// API methods
export const apiService = {
  // Generic methods
  get: (url, config = {}) => api.get(url, config),
  post: (url, data = {}, config = {}) => api.post(url, data, config),
  put: (url, data = {}, config = {}) => api.put(url, data, config),
  patch: (url, data = {}, config = {}) => api.patch(url, data, config),
  delete: (url, config = {}) => api.delete(url, config),

  // File upload with progress
  uploadFile: (url, formData, onUploadProgress = null) => {
    return api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  },

  // Auth methods
  auth: {
    login: (credentials) => api.post('/auth/login', credentials, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      transformRequest: [(data) => {
        const formData = new URLSearchParams();
        Object.keys(data).forEach(key => {
          formData.append(key, data[key]);
        });
        return formData;
      }],
    }),
    register: (userData) => api.post('/auth/register', userData),
    logout: () => api.post('/auth/logout'),
    refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
    getCurrentUser: () => api.get('/auth/me'),
    requestPasswordReset: (email) => api.post('/auth/request-password-reset', { email }),
    resetPassword: (token, newPassword) => api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    }),
    verifyEmail: (token) => api.post('/auth/verify-email', { token }),
  },

  // User methods
  users: {
    getProfile: () => api.get('/users/profile'),
    updateProfile: (userData) => api.patch('/users/profile', userData),
    changePassword: (passwordData) => api.post('/users/change-password', passwordData),
    deleteAccount: () => api.delete('/users/account'),
    getStats: () => api.get('/users/stats'),
  },

  // File methods
  files: {
    getAll: (params = {}) => api.get('/files', { params }),
    getById: (id) => api.get(`/files/${id}`),
    upload: (file, onUploadProgress = null) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiService.uploadFile('/files/upload', formData, onUploadProgress);
    },
    analyze: (file, onUploadProgress = null) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiService.uploadFile('/files/analyze', formData, onUploadProgress);
    },
    delete: (id) => api.delete(`/files/${id}`),
    download: (id) => api.get(`/files/${id}/download`, {
      responseType: 'blob',
    }),
    getMetadata: (id) => api.get(`/files/${id}/metadata`),
  },

  // Analytics methods
  analytics: {
    getResults: (params = {}) => api.get('/analytics/results', { params }),
    getResultById: (id) => api.get(`/analytics/results/${id}`),
    runAnalysis: (fileId, analysisType = 'basic') => api.post('/analytics/analyze', {
      file_id: fileId,
      analysis_type: analysisType,
    }),
    getInsights: (fileId) => api.get(`/analytics/insights/${fileId}`),
    exportResults: (id, format = 'json') => api.get(`/analytics/results/${id}/export`, {
      params: { format },
      responseType: 'blob',
    }),
  },

  // Subscription/Payment methods
  subscription: {
    getPlans: () => api.get('/subscription/plans'),
    getCurrentPlan: () => api.get('/subscription/current'),
    createCheckoutSession: (priceId) => api.post('/subscription/checkout', {
      price_id: priceId,
    }),
    createPortalSession: () => api.post('/subscription/portal'),
    cancelSubscription: () => api.post('/subscription/cancel'),
  },

  // System methods
  system: {
    health: () => axios.get(`${API_BASE_URL}/health`),
    metrics: () => api.get('/system/metrics'),
  },
};

// Helper functions
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.detail || error.response.data?.message || 'Server error';
    return {
      message,
      status: error.response.status,
      data: error.response.data,
    };
  } else if (error.request) {
    // Request was made but no response received
    return {
      message: 'Network error - please check your connection',
      status: 0,
      data: null,
    };
  } else {
    // Something else happened
    return {
      message: error.message || 'An unexpected error occurred',
      status: 0,
      data: null,
    };
  }
};

// Create download link for blob responses
export const createDownloadLink = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export default api;