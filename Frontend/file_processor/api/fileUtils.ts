import axiosInstance from './axiosInstance';
import { 
  UploadFilesResponse, 
  ClearFilesResponse, 
  GetFilesSizeResponse,
  FileContentResponse,
} from '../types/apiTypes';
import handleError from '../utils/handleError';

/**
 * Uploads one or multiple text files.
 * @param {File[]} files - Array of text files to upload.
 * @returns {Promise<UploadFilesResponse>}
 */
export const uploadFiles = async (files: File[]): Promise<UploadFilesResponse> => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('files', file);
  });

  try {
    const response = await axiosInstance.post<UploadFilesResponse>('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Lists all uploaded files.
 * @returns {Promise<string[]>}
 */
export const listFiles = async (): Promise<string[]> => {
  try {
    const response = await axiosInstance.get<string[]>('/files/');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves the content of a specific uploaded file.
 * @param {string} filename - Name of the file.
 * @returns {Promise<FileContentResponse>}
 */
export const getFileContent = async (filename: string): Promise<FileContentResponse> => {
  try {
    const response = await axiosInstance.get<FileContentResponse>(
      `/files/${encodeURIComponent(filename)}`
    );
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Edits the content of a specific uploaded file.
 * @param {string} filename - Name of the file.
 * @param {string} newContent - New content for the file.
 * @returns {Promise<{ message: string }>}.
 */
export const editFileContent = async (
  filename: string,
  newContent: string
): Promise<{ message: string }> => {
  try {
    // Pass new_content as a query parameter
    const response = await axiosInstance.put<{ message: string }>(
      `/files/${encodeURIComponent(filename)}`,
      null,
      { params: { new_content: newContent } }
    );
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};


/**
 * Clears all uploaded files.
 * @returns {Promise<ClearFilesResponse>}
 */
export const clearFiles = async (): Promise<ClearFilesResponse> => {
  try {
    const response = await axiosInstance.delete<ClearFilesResponse>('/files/clear');
    return response.data;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves the total size of uploaded files in bytes.
 * @returns {Promise<number>}
 */
export const getUploadedFilesSize = async (): Promise<number> => {
  try {
    const response = await axiosInstance.get<GetFilesSizeResponse>('/files/size/uploaded');
    return response.data.uploaded_files_size_bytes || 0;
  } catch (error) {
    return handleError(error);
  }
};

/**
 * Retrieves the total size of processed files in bytes.
 * @returns {Promise<number>}
 */
export const getProcessedFilesSize = async (): Promise<number> => {
  try {
    const response = await axiosInstance.get<GetFilesSizeResponse>('/files/size/processed');
    return response.data.processed_files_size_bytes || 0;
  } catch (error) {
    return handleError(error);
  }
};
