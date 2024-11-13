// src/api/promptUtils.ts

import axiosInstance from './axiosInstance';
import { Prompt } from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Retrieves a list of saved prompts.
 * @returns {Promise<string[]>}
 */
export const listPrompts = async (): Promise<string[]> => {
  try {
    const response = await axiosInstance.get<string[]>('/prompts/');
    return response.data;
  } catch (error) {
    return handleError(error); // Adding return here makes TypeScript happy
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
    const response = await axiosInstance.post<{ message: string }>('/prompts/save', prompt);
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
    const response = await axiosInstance.delete<{ message: string }>(`/prompts/${promptName}`);
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};
