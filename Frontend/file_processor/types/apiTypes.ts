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

export interface ErrorLog {
  id: string;
  timestamp: string;
  error_type: string;
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
  files?: string[];  // Added optional files property
}

export interface StartProcessingResponse {
  task_id: string;
  job_id: string;
  message: string;
}

export interface JobProgressFileStatus {
  filename: string;
  status: string;
  processed_chunks: number;
  total_chunks: number;
  progress_percentage: number;
}

export interface GetProcessingProgressResponse {
  job_id: string;
  job_status: string;
  files: JobProgressFileStatus[];
}

export interface TaskStatusResponse {
  task_id: string;
  job_id: string;
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

export interface FileContentResponse {
  filename: string;
  content: string;
}
export interface DeleteFileResponse {
  message: string;
}


export interface LocalUsage {
  max_rpm: number;
  max_rph: number;
  current_rpm: number;
  current_rph: number;
  reset_time_rpm: number;
  reset_time_rph: number;
  cooldown_period: number;
  last_retry_after: string | null;
}

export interface AnthropicUsage {
  requests_limit: number;
  requests_remaining: number;
  requests_reset_time: string; // ISO 8601 format
  tokens_limit: number;
  tokens_remaining: number;
  tokens_reset_time: string; // ISO 8601 format
  input_tokens_limit: number;
  input_tokens_remaining: number;
  input_tokens_reset_time: string; // ISO 8601 format
  output_tokens_limit: number;
  output_tokens_remaining: number;
  output_tokens_reset_time: string; // ISO 8601 format
}

export interface UsageResponse {
  local_usage: LocalUsage;
  anthropic_usage: AnthropicUsage;
}
