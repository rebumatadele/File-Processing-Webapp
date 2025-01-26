// src/api/processingUtils.ts

import axiosInstance from './axiosInstance';
import { 
  GetProcessingProgressResponse,
  ProcessingSettings, 
  StartProcessingResponse, 
  TaskStatusResponse 
} from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Starts processing of uploaded text files.
 * @param {ProcessingSettings} settings - Settings for processing.
 * @returns {Promise<StartProcessingResponse>}
 */
export const startProcessing = async (settings: ProcessingSettings): Promise<StartProcessingResponse> => {
  try {
    const response = await axiosInstance.post<StartProcessingResponse>('/processing/start', settings);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves the status of a specific processing task.
 * @param {string} taskId - ID of the task.
 * @returns {Promise<TaskStatusResponse>}
 */
export const getTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  try {
    const response = await axiosInstance.get<TaskStatusResponse>(`/processing/status/${taskId}`);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves detailed progress for a specific job.
 * @param {string} jobId - ID of the job.
 * @returns {Promise<GetProcessingProgressResponse>}
 */
export const getProcessingProgress = async (jobId: string): Promise<GetProcessingProgressResponse> => {
  try {
    const response = await axiosInstance.get<GetProcessingProgressResponse>(`/processing/progress/${jobId}`);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};