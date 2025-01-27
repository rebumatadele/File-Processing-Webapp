// src/api/resetPasswordInstance.ts

import axios, { AxiosInstance } from 'axios';

const resetPasswordInstance: AxiosInstance = axios.create({
  baseURL: 'https://file-processing-webapp.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

// No interceptors are added to this instance to avoid conflicts

export default resetPasswordInstance;
