// src/api/cacheUtils.ts

import axiosInstance from './axiosInstance';
import { ClearCacheResponse } from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Clears the application cache.
 * @returns {Promise<ClearCacheResponse>}
 */
export const clearCache = async (): Promise<ClearCacheResponse> => {
  try {
    const response = await axiosInstance.post<ClearCacheResponse>('/cache/clear');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
