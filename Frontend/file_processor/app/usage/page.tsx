// src/pages/UsagePage.tsx

'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useToast } from '@/hooks/use-toast'
import { clearCache, getCacheSize, listCacheContents } from '@/api/cacheUtils'
import { clearFiles, listFiles, getFileContent } from '@/api/fileUtils'
import { getAllResults } from '@/api/resultsUtils'
import { getAnthropicUsage } from '@/api/usageUtils' // Newly added
import { ProcessingResult, UsageResponse } from '@/types/apiTypes'
import { FileIcon, DatabaseIcon, CpuIcon, RefreshCw } from 'lucide-react'

export default function UsagePage() {
  // Existing States
  const [cacheMessage, setCacheMessage] = useState<string>('')
  const [fileMessage, setFileMessage] = useState<string>('')
  const [cacheSize, setCacheSize] = useState<number | null>(null)
  const [cacheContents, setCacheContents] = useState<string[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [uploadedFilesSize, setUploadedFilesSize] = useState<number | null>(null)
  const [processedFiles, setProcessedFiles] = useState<ProcessingResult[]>([])
  const [processedFilesSize, setProcessedFilesSize] = useState<number | null>(null)
  const [loadingCache, setLoadingCache] = useState<boolean>(false)
  const [loadingFiles, setLoadingFiles] = useState<boolean>(false)
  const [loadingProcessed, setLoadingProcessed] = useState<boolean>(false)
  
  // New States for Hydration Fix and Anthropic Usage
  const [lastUpdated, setLastUpdated] = useState<string>('')
  const [anthropicUsage, setAnthropicUsage] = useState<UsageResponse | null>(null)
  const [loadingAnthropicUsage, setLoadingAnthropicUsage] = useState<boolean>(false)
  const [lastUpdatedAnthropic, setLastUpdatedAnthropic] = useState<string>('')

  const { toast } = useToast()

  // Fetch Cache Information
  const fetchCacheInfo = async () => {
    setLoadingCache(true)
    try {
      const sizeResponse = await getCacheSize()
      setCacheSize(sizeResponse.cache_size_bytes)
      const contentsResponse = await listCacheContents()
      setCacheContents(contentsResponse.cache_contents)
    } catch (error) {
      console.error("Failed to fetch cache info:", error)
      toast({
        title: 'Error',
        description: 'Failed to fetch cache information.',
        variant: 'destructive',
      })
    } finally {
      setLoadingCache(false)
    }
  }

  // Fetch Uploaded Files Information
  const fetchUploadedFiles = async () => {
    setLoadingFiles(true)
    try {
      const files = await listFiles()
      setUploadedFiles(files)
      let totalSize = 0
      for (const filename of files) {
        const fileInfo = await getFileContent(filename)
        const size = new Blob([fileInfo.content]).size
        totalSize += size
      }
      setUploadedFilesSize(totalSize)
    } catch (error) {
      console.error("Failed to fetch uploaded files:", error)
      toast({
        title: 'Error',
        description: 'Failed to fetch uploaded files.',
        variant: 'destructive',
      })
    } finally {
      setLoadingFiles(false)
    }
  }

  // Fetch Processed Files Information
  const fetchProcessedFiles = async () => {
    setLoadingProcessed(true)
    try {
      const resultsResponse = await getAllResults()
      const results: ProcessingResult[] = Object.entries(resultsResponse).map(([filename, content]) => ({
        filename,
        content,
      }))
      setProcessedFiles(results)
      let totalSize = 0
      results.forEach(result => {
        totalSize += new Blob([result.content]).size
      })
      setProcessedFilesSize(totalSize)
    } catch (error) {
      console.error("Failed to fetch processed files:", error)
      toast({
        title: 'Error',
        description: 'Failed to fetch processed files.',
        variant: 'destructive',
      })
    } finally {
      setLoadingProcessed(false)
    }
  }

  // Fetch Anthropic Usage Information
  const fetchAnthropicUsage = async () => {
    setLoadingAnthropicUsage(true)
    try {
      const usageData = await getAnthropicUsage()
      setAnthropicUsage(usageData)
      setLastUpdatedAnthropic(new Date().toLocaleString())
    } catch (error) {
      console.error("Failed to fetch Anthropic usage:", error)
      toast({
        title: 'Error',
        description: 'Failed to fetch Anthropic usage metrics.',
        variant: 'destructive',
      })
    } finally {
      setLoadingAnthropicUsage(false)
    }
  }

  // Initial Data Fetch
  useEffect(() => {
    fetchCacheInfo()
    fetchUploadedFiles()
    fetchProcessedFiles()
    fetchAnthropicUsage()
    setLastUpdated(new Date().toLocaleString())
  }, [])

  // Handlers to Clear Cache and Files
  const handleClearCache = async () => {
    try {
      setCacheMessage('Clearing cache...')
      const response = await clearCache()
      setCacheMessage(response.message || 'Cache cleared successfully.')
      fetchCacheInfo()
      toast({
        title: 'Cache Cleared',
        description: response.message,
      })
    } catch (error) {
      console.error("Failed to clear cache:", error)
      setCacheMessage('Failed to clear cache.')
      toast({
        title: 'Error',
        description: 'Failed to clear cache.',
        variant: 'destructive',
      })
    }
  }

  const handleClearFiles = async () => {
    try {
      setFileMessage('Clearing files...')
      const response = await clearFiles()
      setFileMessage(response.message || 'All files cleared successfully.')
      fetchUploadedFiles()
      fetchProcessedFiles()
      toast({
        title: 'Files Cleared',
        description: response.message,
      })
    } catch (error) {
      console.error("Failed to clear files:", error)
      setFileMessage('Failed to clear files.')
      toast({
        title: 'Error',
        description: 'Failed to clear files.',
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="container mx-auto p-4 space-y-8">
      <h1 className="text-3xl font-bold text-primary">Usage Information</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Cache Usage */}
        <Card className="shadow-lg">
          <CardHeader className="bg-primary/10 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <DatabaseIcon className="text-primary" />
              <h2 className="text-xl font-semibold">Cache Usage</h2>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <p className="text-lg font-medium">
                Cache Size:{' '}
                {loadingCache ? (
                  <Skeleton className="h-4 w-24 inline-block" />
                ) : (
                  <span className="text-primary">
                    {cacheSize !== null ? `${(cacheSize / 1024).toFixed(2)} KB` : 'N/A'}
                  </span>
                )}
              </p>
              <div>
                <h3 className="text-md font-medium mb-2">Cache Contents:</h3>
                <ScrollArea className="h-40 rounded-md border p-2">
                  {loadingCache ? (
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                    </div>
                  ) : cacheContents.length > 0 ? (
                    cacheContents.map((item, index) => (
                      <p key={index} className="text-sm py-1">
                        {item}
                      </p>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No cache entries.</p>
                  )}
                </ScrollArea>
              </div>
            </div>
          </CardContent>
          <CardFooter className="bg-primary/5 rounded-b-lg flex flex-col items-start space-y-2">
            <Button onClick={handleClearCache} variant="outline" className="w-full">
              Clear Cache
            </Button>
            {cacheMessage && <p className="text-sm text-muted-foreground">{cacheMessage}</p>}
          </CardFooter>
        </Card>

        {/* Anthropic Usage */}
        <Card className="shadow-lg">
          <CardHeader className="bg-purple-100 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <CpuIcon className="text-purple-500" />
              <h2 className="text-xl font-semibold">Anthropic Usage</h2>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              {loadingAnthropicUsage ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                </div>
              ) : anthropicUsage ? (
                <div className="space-y-2">
                  <div>
                    <h3 className="font-medium">Requests:</h3>
                    <p className="text-sm">
                      Limit: {anthropicUsage.anthropic_usage.requests_limit} | Remaining: {anthropicUsage.anthropic_usage.requests_remaining} | Reset Time: {new Date(anthropicUsage.anthropic_usage.requests_reset_time).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-medium">Tokens:</h3>
                    <p className="text-sm">
                      Limit: {anthropicUsage.anthropic_usage.tokens_limit} | Remaining: {anthropicUsage.anthropic_usage.tokens_remaining} | Reset Time: {new Date(anthropicUsage.anthropic_usage.tokens_reset_time).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-medium">Input Tokens:</h3>
                    <p className="text-sm">
                      Limit: {anthropicUsage.anthropic_usage.input_tokens_limit} | Remaining: {anthropicUsage.anthropic_usage.input_tokens_remaining} | Reset Time: {new Date(anthropicUsage.anthropic_usage.input_tokens_reset_time).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <h3 className="font-medium">Output Tokens:</h3>
                    <p className="text-sm">
                      Limit: {anthropicUsage.anthropic_usage.output_tokens_limit} | Remaining: {anthropicUsage.anthropic_usage.output_tokens_remaining} | Reset Time: {new Date(anthropicUsage.anthropic_usage.output_tokens_reset_time).toLocaleString()}
                    </p>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No Anthropic usage data available.</p>
              )}
            </div>
          </CardContent>
          <CardFooter className="bg-purple-50 rounded-b-lg flex justify-between items-center text-sm text-muted-foreground">
            <span>Last updated: {lastUpdatedAnthropic || 'Fetching...'}</span>
            <Button onClick={fetchAnthropicUsage} variant="ghost" size="sm" disabled={loadingAnthropicUsage}>
              <RefreshCw className="h-4 w-4 mr-1" />
              {loadingAnthropicUsage ? 'Refreshing...' : 'Refresh'}
            </Button>
          </CardFooter>
        </Card>

        {/* File Storage Usage */}
        <Card className="shadow-lg">
          <CardHeader className="bg-secondary/10 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <FileIcon className="text-secondary" />
              <h2 className="text-xl font-semibold">File Storage Usage</h2>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <p className="text-lg font-medium">
                Uploaded Files Size:{' '}
                {loadingFiles ? (
                  <Skeleton className="h-4 w-24 inline-block" />
                ) : (
                  <span className="text-primary">
                    {uploadedFilesSize !== null ? `${(uploadedFilesSize / 1024).toFixed(2)} KB` : 'N/A'}
                  </span>
                )}
              </p>
              <div>
                <h3 className="text-md font-medium mb-2">Uploaded Files:</h3>
                <ScrollArea className="h-40 rounded-md border p-2">
                  {loadingFiles ? (
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                    </div>
                  ) : uploadedFiles.length > 0 ? (
                    uploadedFiles.map((file, index) => (
                      <p key={index} className="text-sm py-1">
                        {file}
                      </p>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No uploaded files.</p>
                  )}
                </ScrollArea>
              </div>
            </div>
          </CardContent>
          <CardFooter className="bg-secondary/5 rounded-b-lg flex flex-col items-start space-y-2">
            <Button onClick={handleClearFiles} variant="outline" className="w-full">
              Clear All Files
            </Button>
            {fileMessage && <p className="text-sm text-muted-foreground">{fileMessage}</p>}
          </CardFooter>
        </Card>

        {/* Processed Files */}
        <Card className="shadow-lg">
          <CardHeader className="bg-accent/10 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <CpuIcon className="text-accent" />
              <h2 className="text-xl font-semibold">Processed Files</h2>
            </div>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <p className="text-lg font-medium">
                Processed Files Size:{' '}
                {loadingProcessed ? (
                  <Skeleton className="h-4 w-24 inline-block" />
                ) : (
                  <span className="text-accent">
                    {processedFilesSize !== null ? `${(processedFilesSize / 1024).toFixed(2)} KB` : 'N/A'}
                  </span>
                )}
              </p>
              <div>
                <h3 className="text-md font-medium mb-2">Processed Files:</h3>
                <ScrollArea className="h-40 rounded-md border p-2">
                  {loadingProcessed ? (
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                    </div>
                  ) : processedFiles.length > 0 ? (
                    processedFiles.map((file, index) => (
                      <p key={index} className="text-sm py-1">
                        {file.filename}
                      </p>
                    ))
                  ) : (
                    <p className="text-sm text-muted-foreground">No processed files.</p>
                  )}
                </ScrollArea>
              </div>
            </div>
          </CardContent>
          <CardFooter className="bg-accent/5 rounded-b-lg flex justify-between items-center text-sm text-muted-foreground">
            <span>Last updated: {lastUpdated || 'Fetching...'}</span>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
