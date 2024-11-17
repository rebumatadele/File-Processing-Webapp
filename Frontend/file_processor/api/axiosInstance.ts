// src/api/axiosInstance.ts

import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'https://file-processing-webapp.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the access token in headers
axiosInstance.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default axiosInstance;
