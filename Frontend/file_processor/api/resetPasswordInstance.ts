// src/api/resetPasswordInstance.ts

import axios, { AxiosInstance } from 'axios';

const resetPasswordInstance: AxiosInstance = axios.create({
  baseURL: process.env.BACKEND_URL || 'https://fileprocessingwebapp.onrender.com',
  headers: {
    'Content-Type': 'application/json',
  },
});

// No interceptors are added to this instance to avoid conflicts

export default resetPasswordInstance;
