// src/types/apiTypes.ts

export interface ConfigRequest {
  provider_choice: 'OpenAI' | 'Anthropic' | 'Gemini';
  selected_model: string;
  api_key: string;
}

export interface ConfigResponse {
  message: string;
}

export interface UploadedFileInfo {
  filename: string;
  content: string;
}

export interface UploadFilesResponse {
  message: string;
}

export interface EditFileContentRequest {
  new_content: string;
}

export interface ClearFilesResponse {
  message: string;
}

export interface ClearCacheResponse {
  message: string;
}

export interface ClearErrorsResponse {
  message: string;
}

export interface ProcessingSettings {
  openai_api_key?: string;
  anthropic_api_key?: string;
  gemini_api_key?: string;
  provider_choice: 'OpenAI' | 'Anthropic' | 'Gemini';
  prompt: string;
  chunk_size: number;
  chunk_by: string;
  selected_model: string;
  email: string;
}

export interface StartProcessingResponse {
  task_id: string;
  message: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
}

export interface Prompt {
  name: string;
  content: string;
}

export interface ProcessingResult {
  filename: string;
  content: string;
}

export interface GetAllResultsResponse {
  [filename: string]: string;
}

export interface ClearCacheResponse {
  message: string;
}

export interface CacheSizeResponse {
  cache_size_bytes: number;
}

export interface CacheContentsResponse {
  cache_contents: string[];
}
// src/types/apiTypes.ts

export interface SaveUserConfigRequest {
  user_id: string;
  openai_api_key?: string;
  anthropic_api_key?: string;
  gemini_api_key?: string;
}

export interface SaveUserConfigResponse {
  message: string;
}

export interface GetUserConfigResponse {
  user_id: string;
  openai_api_key?: string;
  anthropic_api_key?: string;
  gemini_api_key?: string;
}


export interface GetFilesSizeResponse {
  uploaded_files_size_bytes?: number;
  processed_files_size_bytes?: number;
}

export interface StartBatchProcessingRequest {
  prompt: string;
  chunk_size: number;
  chunk_by: 'word' | 'character';
  selected_model: string;
  email?: string;
  anthropic_api_key?: string;
}

export interface StartBatchProcessingResponse {
  batch_id: string;
  message: string;
}

export interface BatchStatusResponse {
  batch_id: string;
  processing_status: string;
  request_counts: Record<string, number>;
  created_at?: string;
  ended_at?: string;
  expires_at?: string;
  results_url?: string;
}

export interface CancelBatchResponse {
  batch_id: string;
  message: string;
}

export interface BatchListResponse {
  [batch_id: string]: BatchStatusResponse;
}
