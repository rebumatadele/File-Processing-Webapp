// src/api/usageUtils.ts

import axiosInstance from './axiosInstance'
import { UsageResponse } from '../types/apiTypes'
import handleError from '../utils/handleError'

/**
 * Retrieves usage information for Anthropic.
 * @returns {Promise<UsageResponse>}
 */
export const getAnthropicUsage = async (): Promise<UsageResponse> => {
  try {
    const response = await axiosInstance.get<UsageResponse>('/usage')
    return response.data
  } catch (error) {
    return handleError(error)
  }
}
