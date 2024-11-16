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
import { AlertTriangleIcon, RefreshCwIcon, TrashIcon } from 'lucide-react'

export default function ErrorLogsPage() {
  const [errors, setErrors] = useState<string[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [clearing, setClearing] = useState<boolean>(false)
  const { toast } = useToast()

  const fetchErrors = async () => {
    setLoading(true)
    try {
      const data = await getErrorLogs()
      setErrors(data)
    } catch {
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
      toast({
        title: 'Logs Cleared',
        description: data.message,
      })
    } catch {
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
            <AlertTriangleIcon className="text-destructive h-6 w-6" />
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
              <RefreshCwIcon className="h-4 w-4" />
              <span>{loading ? 'Refreshing...' : 'Refresh'}</span>
            </Button>
            <Button
              variant="destructive"
              onClick={handleClearErrors}
              disabled={clearing}
              className="flex items-center space-x-2"
            >
              <TrashIcon className="h-4 w-4" />
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
                <AlertTriangleIcon className="h-12 w-12 mb-2" />
                <p>No error logs available.</p>
              </div>
            ) : (
              <ul className="space-y-2">
                {errors.map((error, index) => (
                  <li key={index} className="bg-destructive/10 text-destructive rounded-md p-3 text-sm">
                    {error}
                  </li>
                ))}
              </ul>
            )}
          </ScrollArea>
        </CardContent>
        <CardFooter className="bg-muted/50 rounded-b-lg flex justify-between items-center text-sm text-muted-foreground">
          <span>Last updated: {new Date().toLocaleString()}</span>
          <span>{errors.length} error{errors.length !== 1 ? 's' : ''} logged</span>
        </CardFooter>
      </Card>
    </div>
  )
}