// src/utils/handleError.ts

import axios, { AxiosError } from 'axios';

/**
 * Handles errors from Axios requests and throws an Error with a detailed message.
 * @param {unknown} error - The error thrown.
 * @returns {never} - This function always throws an error, so it never returns.
 */
const handleError = (error: unknown): never => {
  let errorMessage = 'An unexpected error occurred';

  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;

    // Check if response and response data exist and have expected structure
    errorMessage = axiosError.response?.data && typeof axiosError.response.data === 'object'
      ? (axiosError.response.data as { detail?: string; message?: string }).detail || 
        (axiosError.response.data as { detail?: string; message?: string }).message ||
        axiosError.message
      : axiosError.message;
  }

  throw new Error(errorMessage);
};

export default handleError;
