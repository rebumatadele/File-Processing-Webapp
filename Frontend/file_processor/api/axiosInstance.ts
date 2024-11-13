// src/api/axiosInstance.ts

import axios from 'axios';
const axiosInstance = axios.create({
  baseURL: 'https://file-processing-webapp.onrender.com', // Fallback to localhost
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;
