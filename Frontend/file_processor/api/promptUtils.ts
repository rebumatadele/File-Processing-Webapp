// src/api/promptUtils.ts

import axiosInstance from './axiosInstance';
import { Prompt } from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Retrieves a paginated list of saved prompts with optional search and filter criteria.
 * @param {string | undefined} search - Search term for prompt names.
 * @param {string[] | undefined} tags - Tags to filter prompts.
 * @param {number} page - Page number for pagination (default: 1).
 * @param {number} size - Number of prompts per page (default: 10).
 * @returns {Promise<{ prompts: string[]; total: number; page: number; size: number }>}
 */
export const listPrompts = async (
  search?: string,
  tags?: string[],
  page: number = 1,
  size: number = 10
): Promise<{ prompts: string[]; total: number; page: number; size: number }> => {
  try {
    const params: Record<string, string | number> = { page, size };
    if (search) params.search = search;
    if (tags) params.tags = tags.join(',');

    const response = await axiosInstance.get('/prompts/', { params });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Loads a specific prompt by name.
 * @param {string} promptName - Name of the prompt.
 * @returns {Promise<Prompt>}
 */
export const loadPrompt = async (promptName: string): Promise<Prompt> => {
  try {
    const response = await axiosInstance.get<Prompt>(`/prompts/${promptName}`);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Saves a new prompt or overwrites an existing one.
 * @param {Prompt} prompt - Prompt data to save.
 * @returns {Promise<{ message: string }>}
 */
export const savePrompt = async (prompt: Prompt): Promise<{ message: string }> => {
  try {
    const response = await axiosInstance.post('/prompts/save', prompt);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Updates an existing prompt by name.
 * @param {string} promptName - Name of the prompt to update.
 * @param {Partial<Prompt>} updates - Fields to update in the prompt.
 * @returns {Promise<{ message: string }>}
 */
export const updatePrompt = async (
  promptName: string,
  updates: Partial<Prompt>
): Promise<{ message: string }> => {
  try {
    const response = await axiosInstance.put(`/prompts/${promptName}`, updates);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Deletes a specific prompt by name.
 * @param {string} promptName - Name of the prompt to delete.
 * @returns {Promise<{ message: string }>}
 */
export const deletePrompt = async (promptName: string): Promise<{ message: string }> => {
  try {
    const response = await axiosInstance.delete(`/prompts/${promptName}`);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Bulk deletes prompts by their names.
 * @param {string[]} promptNames - Array of prompt names to delete.
 * @returns {Promise<{ message: string }>}
 */
export const bulkDeletePrompts = async (promptNames: string[]): Promise<{ message: string }> => {
  try {
    const response = await axiosInstance.post('/prompts/bulk_delete', { prompt_names: promptNames });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
