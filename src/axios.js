// src/axios.js
import axios from 'axios';

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // e.g., "http://localhost:5000/api" (no trailing slash)
  withCredentials: true,  // Include cookies if needed
});

// Request interceptor (attach token if available)
instance.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor for token refresh (handles 401 errors)
instance.interceptors.response.use(
  response => response,
  async error => {
    // Check for 401 error (Token expired)
    const originalRequest = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      error.response.data.msg === 'Token has expired' &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          window.location.href = '/login';
          return Promise.reject(error);
        }
        const { data } = await instance.post('/refresh', null, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });
        localStorage.setItem('access_token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return instance(originalRequest);
      } catch (refreshError) {
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Additional response interceptor for maintenance mode (handles 503 errors)
// If a 503 response is returned, the user is immediately redirected to the maintenance page.
instance.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 503) {
      // Prevent redirect loop: only redirect if not already on /maintenance.
      if (window.location.pathname !== '/maintenance') {
        window.location.href = '/maintenance';
      }
    }
    return Promise.reject(error);
  }
);

export default instance;
