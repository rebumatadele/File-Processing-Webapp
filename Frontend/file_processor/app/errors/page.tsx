// src/pages/ErrorLogsPage.tsx

'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  CardFooter
} from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useToast } from '@/hooks/use-toast'
import { getErrorLogs, clearErrors } from '../../api/errorUtils'
import { AlertTriangle, RefreshCw, Trash2 } from 'lucide-react'
import { ErrorLog } from '@/types/apiTypes'

export default function ErrorLogsPage() {
  const [errors, setErrors] = useState<ErrorLog[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [clearing, setClearing] = useState<boolean>(false)
  const { toast } = useToast()
  
  // New state for client-side only 'lastUpdated' timestamp
  const [lastUpdated, setLastUpdated] = useState<string>('')

  const fetchErrors = async () => {
    setLoading(true)
    try {
      const data = await getErrorLogs()
      setErrors(data)
      // Update 'lastUpdated' after successful fetch
      setLastUpdated(new Date().toLocaleString())
    } catch (error) {
      console.error("Failed to fetch error logs:", error)
      toast({
        title: 'Error',
        description: 'Failed to fetch error logs.',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleClearErrors = async () => {
    setClearing(true)
    try {
      const data = await clearErrors()
      setErrors([])
      setLastUpdated(new Date().toLocaleString()) // Update timestamp after clearing
      toast({
        title: 'Logs Cleared',
        description: data.message,
      })
    } catch (error) {
      console.error("Failed to clear error logs:", error)
      toast({
        title: 'Error',
        description: 'Failed to clear error logs.',
        variant: 'destructive',
      })
    } finally {
      setClearing(false)
    }
  }

  useEffect(() => {
    fetchErrors()
  }, [])

  return (
    <div className="container mx-auto py-10 min-h-screen flex items-center justify-center">
      <Card className="w-full max-w-4xl">
        <CardHeader className="bg-destructive/10 rounded-t-lg">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="text-destructive h-6 w-6" />
            <CardTitle className="text-2xl font-bold">Error Logs</CardTitle>
          </div>
          <CardDescription className="text-destructive-foreground/80">
            View and manage application error logs.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="flex justify-between items-center mb-4">
            <Button
              variant="outline"
              onClick={fetchErrors}
              disabled={loading}
              className="flex items-center space-x-2"
            >
              <RefreshCw className="h-4 w-4" />
              <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
            </Button>
            <Button
              variant="destructive"
              onClick={handleClearErrors}
              disabled={clearing || errors.length === 0}
              className="flex items-center space-x-2"
            >
              <Trash2 className="h-4 w-4" />
              <span>{clearing ? 'Clearing...' : 'Clear Logs'}</span>
            </Button>
          </div>
          <ScrollArea className="h-[400px] rounded-md border p-4">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
              </div>
            ) : errors.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <AlertTriangle className="h-12 w-12 mb-2" />
                <p>No error logs available.</p>
              </div>
            ) : (
              <ul className="space-y-2">
                {errors.map((error) => (
                  <li key={error.id} className="bg-destructive/10 text-destructive rounded-md p-3 text-sm">
                    <div className="flex flex-col">
                      <span className="font-semibold">[{new Date(error.timestamp).toLocaleString()}] {error.error_type}</span>
                      <span className="mt-1">{error.message}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </ScrollArea>
        </CardContent>
        <CardFooter className="bg-muted/50 rounded-b-lg flex justify-between items-center text-sm text-muted-foreground">
          <span>Last updated: {lastUpdated || 'Fetching...'}</span>
          <span>{errors.length} error{errors.length !== 1 ? 's' : ''} logged</span>
        </CardFooter>
      </Card>
    </div>
  )
}