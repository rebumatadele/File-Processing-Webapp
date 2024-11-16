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

/**
 * Retrieves the total cache size in bytes.
 * @returns {Promise<{ cache_size_bytes: number }>}
 */
export const getCacheSize = async (): Promise<{ cache_size_bytes: number }> => {
  try {
    const response = await axiosInstance.get<{ cache_size_bytes: number }>('/cache/size');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Lists all cache contents.
 * @returns {Promise<{ cache_contents: string[] }>}
 */
export const listCacheContents = async (): Promise<{ cache_contents: string[] }> => {
  try {
    const response = await axiosInstance.get<{ cache_contents: string[] }>('/cache/contents');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
