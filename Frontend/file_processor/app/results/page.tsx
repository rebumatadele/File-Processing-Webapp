'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import { Loader2, FileText, Download, RefreshCw, ClipboardCheck } from 'lucide-react'
import { getAllResults, getResult, downloadResult } from '@/api/resultsUtils'
import { ProcessingResult } from '@/types/apiTypes'

export default function ResultsPage() {
  const [results, setResults] = useState<string[]>([])
  const [selectedResult, setSelectedResult] = useState<ProcessingResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const { toast } = useToast()

  useEffect(() => {
    fetchResults()
  }, [])

  const fetchResults = async () => {
    setIsLoading(true)
    try {
      const response = await getAllResults()
      const filenames = Object.keys(response)
      setResults(filenames)
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch results. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handlePreviewResult = async (filename: string) => {
    setIsLoading(true)
    try {
      const result = await getResult(filename)
      setSelectedResult(result)
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch result preview. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadResult = async (filename: string) => {
    setIsLoading(true)
    try {
      const blob = await downloadResult(filename)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      window.URL.revokeObjectURL(url)
      toast({
        title: "Success",
        description: "Result downloaded successfully.",
      })
    } catch {
      toast({
        title: "Error",
        description: "Failed to download result. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopyContent = () => {
    if (selectedResult) {
      navigator.clipboard.writeText(selectedResult.content)
      toast({
        title: "Copied",
        description: "Result content copied to clipboard.",
      })
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader className="bg-primary/10 rounded-t-lg">
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <FileText className="h-6 w-6 text-primary" />
            Processing Results
          </CardTitle>
          <CardDescription>View and download your processing results</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="h-[500px] flex flex-col">
              <CardHeader className="bg-muted/50">
                <CardTitle className="text-lg font-semibold flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-primary" />
                    Results List
                  </span>
                  <Button variant="ghost" size="sm" onClick={fetchResults} disabled={isLoading}>
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-grow overflow-hidden p-0">
                <ScrollArea className="h-full p-4">
                  {results.length === 0 ? (
                    <p className="text-muted-foreground text-center py-4">No results available.</p>
                  ) : (
                    results.map((filename) => (
                      <Button
                        key={filename}
                        variant="ghost"
                        className="w-full justify-start mb-2"
                        onClick={() => handlePreviewResult(filename)}
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        {filename}
                      </Button>
                    ))
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            <Card className="h-[500px] flex flex-col">
              <CardHeader className="bg-muted/50">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Result Preview
                </CardTitle>
                <CardDescription>
                  {selectedResult ? selectedResult.filename : "Select a result to preview"}
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-grow overflow-hidden p-4">
                <ScrollArea className="h-full">
                  {selectedResult ? (
                    <pre className="whitespace-pre-wrap text-sm">{selectedResult.content}</pre>
                  ) : (
                    <p className="text-muted-foreground text-center py-4">No result selected.</p>
                  )}
                </ScrollArea>
              </CardContent>
              <CardFooter className="bg-muted/30 rounded-b-lg flex justify-between items-center p-2">
                {selectedResult && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleCopyContent}
                      disabled={isLoading}
                    >
                      <ClipboardCheck className="mr-2 h-4 w-4" />
                      Copy Content
                    </Button>
                    <Button
                      onClick={() => handleDownloadResult(selectedResult.filename)}
                      disabled={isLoading}
                      size="sm"
                    >
                      {isLoading ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Download className="mr-2 h-4 w-4" />
                      )}
                      Download
                    </Button>
                  </>
                )}
              </CardFooter>
            </Card>
          </div>
        </CardContent>
      </Card>

      {isLoading && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center">
          <Card className="w-[300px]">
            <CardContent className="flex items-center justify-center p-6">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="ml-4 text-lg font-medium">Loading...</p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}