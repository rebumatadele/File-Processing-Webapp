// src/api/errorUtils.ts

import axiosInstance from './axiosInstance';
import { ClearErrorsResponse, ErrorLog } from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Retrieves the list of error logs.
 * @returns {Promise<ErrorLog[]>}
 */
export const getErrorLogs = async (): Promise<ErrorLog[]> => {
  try {
    const response = await axiosInstance.get<ErrorLog[]>('/errors/');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Clears all error logs.
 * @returns {Promise<ClearErrorsResponse>}
 */
export const clearErrors = async (): Promise<ClearErrorsResponse> => {
  try {
    const response = await axiosInstance.delete<ClearErrorsResponse>('/errors/');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
