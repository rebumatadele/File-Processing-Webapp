// src/pages/UsagePage.tsx

"use client"

import React, { useState, useEffect } from "react"
import { useToast } from "@/hooks/use-toast"
import { CacheUsageCard } from "@/components/usage/cache-usage-card"
import { AnthropicUsageCard } from "@/components/usage/anthropic-usage-card"
import { FileStorageCard } from "@/components/usage/file-storage-card"
import { ProcessedFilesCard } from "@/components/usage/processed-files-card"
import { clearCache, getCacheSize, listCacheContents } from "@/api/cacheUtils"
import { clearFiles, listFiles, getUploadedFilesSize, getProcessedFilesSize } from "@/api/fileUtils" // Updated import
import { getAllResults } from "@/api/resultsUtils"
import { getAnthropicUsage } from "@/api/usageUtils"
import {
  type CacheSizeResponse,
  type CacheContentsResponse,
  type ClearCacheResponse,
  type ClearFilesResponse,
  type GetAllResultsResponse,
  type UsageResponse,
} from "@/types/apiTypes"

export default function UsagePage() {
  const [lastUpdated, setLastUpdated] = useState<string>("")
  const { toast } = useToast()

  // State for Cache Usage
  const [cacheData, setCacheData] = useState<{ size: number | null; contents: string[] }>({ size: null, contents: [] })
  
  // State for Anthropic Usage
  const [anthropicData, setAnthropicData] = useState<{ anthropic_usage: UsageResponse['anthropic_usage']; last_updated: string } | null>(null)
  
  // State for File Storage
  const [fileData, setFileData] = useState<{ files: string[]; size: number | null }>({ files: [], size: null })
  
  // State for Processed Files
  const [processedData, setProcessedData] = useState<{
    files: { filename: string; content: string }[]
    size: number | null
  }>({ files: [], size: null })

  // Loading States
  const [loading, setLoading] = useState({
    cache: false,
    anthropic: false,
    files: false,
    processed: false,
  })

  /**
   * Fetch Cache Information
   */
  const fetchCacheData = async () => {
    setLoading((prev) => ({ ...prev, cache: true }))
    try {
      const size: CacheSizeResponse = await getCacheSize()
      const contents: CacheContentsResponse = await listCacheContents()
      setCacheData({ size: size.cache_size_bytes, contents: contents.cache_contents })
    } catch (error) {
      console.error("Failed to fetch cache data:", error)
      toast({
        title: "Error",
        description: "Failed to fetch cache information.",
        variant: "destructive",
      })
    } finally {
      setLoading((prev) => ({ ...prev, cache: false }))
    }
  }

  /**
   * Fetch Anthropic Usage Information
   */
  const fetchAnthropicData = async () => {
    setLoading((prev) => ({ ...prev, anthropic: true }))
    try {
      const usage: UsageResponse = await getAnthropicUsage()
      setAnthropicData({
        anthropic_usage: usage.anthropic_usage,
        last_updated: new Date().toLocaleString(),
      })
    } catch (error) {
      console.error("Failed to fetch Anthropic usage:", error)
      toast({
        title: "Error",
        description: "Failed to fetch Anthropic usage information.",
        variant: "destructive",
      })
    } finally {
      setLoading((prev) => ({ ...prev, anthropic: false }))
    }
  }

  /**
   * Fetch Uploaded Files Information
   */
  const fetchFileData = async () => {
    setLoading((prev) => ({ ...prev, files: true }))
    try {
      const files: string[] = await listFiles()
      const size: number = await getUploadedFilesSize() // Updated function
      setFileData({
        files,
        size: size || null, // Handle potential undefined or zero
      })
    } catch (error) {
      console.error("Failed to fetch file data:", error)
      toast({
        title: "Error",
        description: "Failed to fetch file information.",
        variant: "destructive",
      })
    } finally {
      setLoading((prev) => ({ ...prev, files: false }))
    }
  }

  /**
   * Fetch Processed Files Information
   */
  const fetchProcessedData = async () => {
    setLoading((prev) => ({ ...prev, processed: true }))
    try {
      const results: GetAllResultsResponse = await getAllResults()
      const files = Object.entries(results).map(([filename, content]) => ({ filename, content }))
      const size: number = await getProcessedFilesSize() // Updated function
      setProcessedData({
        files,
        size: size || null, // Handle potential undefined or zero
      })
    } catch (error) {
      console.error("Failed to fetch processed data:", error)
      toast({
        title: "Error",
        description: "Failed to fetch processed file information.",
        variant: "destructive",
      })
    } finally {
      setLoading((prev) => ({ ...prev, processed: false }))
    }
  }

  /**
   * Handler to Clear Cache
   */
  const handleClearCache = async () => {
    try {
      const response: ClearCacheResponse = await clearCache()
      toast({
        title: "Cache Cleared",
        description: response.message,
      })
      await fetchCacheData()
    } catch (error) {
      console.error("Failed to clear cache:", error)
      toast({
        title: "Error",
        description: "Failed to clear cache.",
        variant: "destructive",
      })
    }
  }

  /**
   * Handler to Clear Files
   */
  const handleClearFiles = async () => {
    try {
      const response: ClearFilesResponse = await clearFiles()
      toast({
        title: "Files Cleared",
        description: response.message,
      })
      await fetchFileData()
      await fetchProcessedData()
    } catch (error) {
      console.error("Failed to clear files:", error)
      toast({
        title: "Error",
        description: "Failed to clear files.",
        variant: "destructive",
      })
    }
  }

  /**
   * Initial Data Fetch
   */
  useEffect(() => {
    fetchCacheData()
    fetchAnthropicData()
    fetchFileData()
    fetchProcessedData()
    setLastUpdated(new Date().toLocaleString())
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Empty dependency array to run once on mount

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold text-primary">Usage Information</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Cache Usage */}
        <CacheUsageCard data={cacheData} loading={loading.cache} onClearCache={handleClearCache} />
        
        {/* Anthropic Usage */}
        <AnthropicUsageCard data={anthropicData} loading={loading.anthropic} onRefresh={fetchAnthropicData} />
        
        {/* File Storage Usage */}
        <FileStorageCard data={fileData} loading={loading.files} onClearFiles={handleClearFiles} />
        
        {/* Processed Files */}
        <ProcessedFilesCard data={processedData} loading={loading.processed} lastUpdated={lastUpdated} />
        
      </div>
    </div>
  )
}