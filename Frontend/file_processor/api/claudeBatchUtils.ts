// src/api/claudeBatchUtils.ts

import axiosInstance from './axiosInstance';
import { 
  StartBatchProcessingRequest, 
  StartBatchProcessingResponse, 
  BatchStatusResponse, 
  CancelBatchResponse, 
  BatchListResponse 
} from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Starts a Claude batch processing task.
 * @param {StartBatchProcessingRequest} request - The batch processing request parameters.
 * @returns {Promise<StartBatchProcessingResponse | void>}
 */
export const startClaudeBatchProcessing = async (
  request: StartBatchProcessingRequest
): Promise<StartBatchProcessingResponse | void> => {
  try {
    const response = await axiosInstance.post<StartBatchProcessingResponse>(
      '/processing/claude/batch_start',
      request
    );
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves the status of a specific Claude batch processing task.
 * @param {string} batchId - The ID of the batch to retrieve status for.
 * @returns {Promise<BatchStatusResponse | void>}
 */
export const getClaudeBatchStatus = async (
  batchId: string
): Promise<BatchStatusResponse | void> => {
  try {
    const response = await axiosInstance.get<BatchStatusResponse>(
      `/processing/claude/batch_status/${batchId}`
    );
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Lists all Claude batch processing tasks.
 * @returns {Promise<BatchListResponse | void>}
 */
export const listClaudeBatches = async (): Promise<BatchListResponse | void> => {
  try {
    const response = await axiosInstance.get<BatchListResponse>(
      '/processing/claude/batch_list'
    );
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Cancels an ongoing Claude batch processing task.
 * @param {string} batchId - The ID of the batch to cancel.
 * @returns {Promise<CancelBatchResponse | void>}
 */
export const cancelClaudeBatch = async (
  batchId: string
): Promise<CancelBatchResponse | void> => {
  try {
    const response = await axiosInstance.post<CancelBatchResponse>(
      `/processing/claude/batch_cancel/${batchId}`
    );
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
