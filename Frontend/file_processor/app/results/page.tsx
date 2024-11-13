'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import { Loader2, FileText, Download } from 'lucide-react'
import { getAllResults, getResult, downloadResult } from '@/api/resultsUtils'
import { ProcessingResult } from '@/types/apiTypes'

export default function ResultsPage() {
  // Initialize results as an array of filenames
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
      // Extract filenames from the response object
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

  return (
    <div className="container mx-auto py-10">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Results List Card */}
        <Card>
          <CardHeader>
            <CardTitle>Results List</CardTitle>
            <CardDescription>Select a result to preview or download</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[400px]">
              {results.length === 0 ? (
                <p>No results available.</p>
              ) : (
                results.map((filename) => (
                  <Button
                    key={filename} // Ensure filenames are unique
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

        {/* Result Preview Card */}
        <Card>
          <CardHeader>
            <CardTitle>Result Preview</CardTitle>
            <CardDescription>
              {selectedResult ? selectedResult.filename : "Select a result to preview"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              {selectedResult ? (
                <pre className="whitespace-pre-wrap">{selectedResult.content}</pre>
              ) : (
                <p>No result selected.</p>
              )}
            </ScrollArea>
          </CardContent>
          <CardFooter>
            {selectedResult && (
              <Button
                onClick={() => handleDownloadResult(selectedResult.filename)}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Download className="mr-2 h-4 w-4" />
                )}
                Download
              </Button>
            )}
          </CardFooter>
        </Card>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-white" />
        </div>
      )}
    </div>
  )
}