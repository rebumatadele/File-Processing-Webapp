'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription
} from '@/components/ui/card'
import { useToast } from '@/hooks/use-toast' // Importing the useToast hook
import { getErrorLogs, clearErrors } from '../../api/errorUtils'

export default function Errors() {
  const [errors, setErrors] = useState<string[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [clearing, setClearing] = useState<boolean>(false)
  
  // Instantiate toast from the useToast hook
  const { toast } = useToast()

  // Fetch errors from the backend
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

  // Clear all error logs
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
    <div className="container mx-auto py-10">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Error Logs</CardTitle>
          <CardDescription>View and manage application error logs.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-4 mb-4">
            <Button variant="secondary" onClick={fetchErrors} disabled={loading}>
              {loading ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button variant="secondary" onClick={handleClearErrors} disabled={clearing}>
              {clearing ? 'Clearing...' : 'Clear Logs'}
            </Button>
          </div>
          {loading ? (
            <p>Loading error logs...</p>
          ) : errors.length === 0 ? (
            <p>No error logs available.</p>
          ) : (
            <ul className="space-y-2">
              {errors.map((error, index) => (
                <li key={index} className="text-red-600">
                  {error}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
