// src/api/fileUtils.ts

import axiosInstance from './axiosInstance'
import handleError from '../utils/handleError'
import {
  UploadFilesResponse,
  ClearFilesResponse,
  GetFilesSizeResponse,
  FileContentResponse,
  DeleteFileResponse,
} from '../types/apiTypes'

// -- Import your XOR helpers:
import {
  readFileAsUint8Array,
  generateRandomKey,
  xorData,
  toBase64,
} from '@/utils/cryptoUtils'

/**
 * Upload files as XOR-encrypted to '/files/upload'.
 * The backend expects fields:
 *    - filename
 *    - encrypted_file
 *    - file_key
 */
export const uploadXorEncryptedFiles = async (
  files: File[]
): Promise<UploadFilesResponse> => {
  try {
    const formData = new FormData()
    // Loop over each File and encrypt it
    for (const file of files) {
      const fileBytes = await readFileAsUint8Array(file)
      const keyBytes = generateRandomKey(fileBytes.length)
      const encryptedBytes = xorData(fileBytes, keyBytes)

      const encryptedBase64 = toBase64(encryptedBytes)
      const keyBase64 = toBase64(keyBytes)

      formData.append('filename', file.name)
      formData.append('encrypted_file', encryptedBase64)
      formData.append('file_key', keyBase64)
    }
    // Send it to the backend
    const response = await axiosInstance.post<UploadFilesResponse>(
      '/files/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )

    return response.data
  } catch (error) {
    return handleError(error)
  }
}

/**
 * Edits the content of a specific uploaded file by generating a new key,
 * encrypting the new content, and sending both to the backend.
 */
export const editFileContentWithNewKey = async (
  filename: string,
  newContent: string
): Promise<{ message: string }> => {
  try {
    console.log("about to update file: ", filename)

    // Encrypt the newContent with a new key
    const fileBytes = new TextEncoder().encode(newContent)
    const keyBytes = generateRandomKey(fileBytes.length)
    const encryptedBytes = xorData(fileBytes, keyBytes)

    const encryptedBase64 = toBase64(encryptedBytes)
    const keyBase64 = toBase64(keyBytes)

    // Send encrypted_content and new_key in the request body
    const response = await axiosInstance.put<{ message: string }>(
      `/files/${encodeURIComponent(filename)}`,
      { encrypted_file: encryptedBase64, file_key: keyBase64 }, // Send as JSON
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )
    console.log("sent the file to the expecting party")
    return response.data
  } catch (error) {
    return handleError(error)
  }
}

/**
 * Lists all uploaded files.
 */
export const listFiles = async (): Promise<string[]> => {
  try {
    const response = await axiosInstance.get<string[]>('/files/')
    return response.data
  } catch (error) {
    return handleError(error)
  }
}

/**
 * Retrieves the content of a specific uploaded file.
 */
export const getFileContent = async (
  filename: string
): Promise<FileContentResponse> => {
  try {
    const response = await axiosInstance.get<FileContentResponse>(
      `/files/${encodeURIComponent(filename)}`
    )
    return response.data
  } catch (error) {
    return handleError(error)
  }
}

/**
 * Clears all uploaded files.
 */
export const clearFiles = async (): Promise<ClearFilesResponse> => {
  try {
    const response = await axiosInstance.delete<ClearFilesResponse>('/files/clear')
    return response.data
  } catch (error) {
    return handleError(error)
  }
}

/**
 * Retrieves the total size of uploaded files in bytes.
 */
export const getUploadedFilesSize = async (): Promise<number> => {
  try {
    const response = await axiosInstance.get<GetFilesSizeResponse>(
      '/files/size/uploaded'
    )
    return response.data.uploaded_files_size_bytes || 0
  } catch (error) {
    return handleError(error)
  }
}

/**
 * Retrieves the total size of processed files in bytes.
 */
export const getProcessedFilesSize = async (): Promise<number> => {
  try {
    const response = await axiosInstance.get<GetFilesSizeResponse>(
      '/files/size/processed'
    )
    return response.data.processed_files_size_bytes || 0
  } catch (error) {
    return handleError(error)
  }
}

/**
 * Deletes a specific uploaded file.
 */
export const deleteFile = async (filename: string): Promise<DeleteFileResponse> => {
  try {
    const response = await axiosInstance.delete<DeleteFileResponse>(
      `/files/${encodeURIComponent(filename)}`
    )
    return response.data
  } catch (error) {
    return handleError(error)
  }
}
