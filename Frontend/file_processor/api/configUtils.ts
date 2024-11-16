// src/api/configUtils.ts

import axiosInstance from './axiosInstance';
import { 
  ConfigRequest, 
  ConfigResponse, 
  SaveUserConfigRequest, 
  SaveUserConfigResponse,
  GetUserConfigResponse
} from '../types/apiTypes';
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
/**
 * Saves a user's configuration, including API keys.
 * @param {SaveUserConfigRequest} userConfig - User configuration data.
 * @returns {Promise<SaveUserConfigResponse>}
 */
export const saveUserConfig = async (userConfig: SaveUserConfigRequest): Promise<SaveUserConfigResponse> => {
  try {
    const response = await axiosInstance.post<SaveUserConfigResponse>('/config/save', userConfig);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves a user's configuration by user ID.
 * @param {string} userId - The user's ID.
 * @returns {Promise<GetUserConfigResponse>}
 */
export const getUserConfig = async (userId: string): Promise<GetUserConfigResponse> => {
  try {
    const response = await axiosInstance.get<GetUserConfigResponse>(`/config/get/${userId}`);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
