// src/api/configUtils.ts

import axiosInstance from './axiosInstance';
import { 
  ConfigRequest, 
  ConfigResponse, 
  GetUserConfigResponse 
} from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Configures and saves the user's AI provider settings.
 * @param {ConfigRequest} config - Configuration data.
 * @returns {Promise<ConfigResponse>}
 */
export const configureProvider = async (config: ConfigRequest): Promise<ConfigResponse> => {
  try {
    // Using the /config/save route as defined by the backend.
    const response = await axiosInstance.post<ConfigResponse>('/config/save', config);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves the current user's configuration.
 * @returns {Promise<GetUserConfigResponse>}
 */
export const getUserConfig = async (): Promise<GetUserConfigResponse> => {
  try {
    const response = await axiosInstance.get<GetUserConfigResponse>('/config/get');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
