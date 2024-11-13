// src/api/configUtils.ts

import axiosInstance from './axiosInstance';
import { ConfigRequest, ConfigResponse } from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Configures the AI provider.
 * @param {ConfigRequest} config - Configuration data.
 * @returns {Promise<ConfigResponse>}
 */
export const configureProvider = async (config: ConfigRequest): Promise<ConfigResponse> => {
  try {
    const response = await axiosInstance.post<ConfigResponse>('/config/configure', config);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
