import axiosInstance from './axiosInstance';
import { 
  ProcessingResult, 
  GetAllResultsResponse 
} from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Retrieves all processed results.
 * @returns {Promise<GetAllResultsResponse>}
 */
export const getAllResults = async (): Promise<GetAllResultsResponse> => {
  try {
    const response = await axiosInstance.get<GetAllResultsResponse>('/results/');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves the processed result for a specific file.
 * @param {string} filename - Name of the file.
 * @returns {Promise<ProcessingResult>}
 */
export const getResult = async (filename: string): Promise<ProcessingResult> => {
  try {
    const response = await axiosInstance.get<ProcessingResult>(`/results/${encodeURIComponent(filename)}`);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Downloads the processed result as a text file.
 * @param {string} filename - Name of the file.
 * @returns {Promise<Blob>}
 */
export const downloadResult = async (filename: string): Promise<Blob> => {
  try {
    const response = await axiosInstance.get(`/results/${encodeURIComponent(filename)}/download`, {
      responseType: 'blob',
    });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
