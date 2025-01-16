'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Loader2, Play, RefreshCw, Eye, EyeOff, Zap, Mail, Layers, SplitSquareVertical, XCircle, Download, Clock, Calendar, AlertTriangle } from 'lucide-react'
import { startClaudeBatchProcessing, getClaudeBatchStatus, listClaudeBatches, cancelClaudeBatch } from '@/api/claudeBatchUtils'
import { listPrompts } from '@/api/promptUtils'
import { StartBatchProcessingRequest, BatchListResponse } from '@/types/apiTypes'
import { getUserConfig } from '@/api/configUtils'
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion"

const formSchema = z.object({
  prompt: z.string().min(1, 'Please select a prompt'),
  chunk_size: z.number().int().positive().min(1, 'Chunk size must be a positive integer'),
  chunk_by: z.enum(['word', 'character']),
  selected_model: z.string().min(1, 'Please select a model'),
  email: z.string().email('Please enter a valid email address'),
  anthropic_api_key: z.string().optional(),
})

const modelOptions = ['claude-3-5-sonnet-20240620', 'claude-3-5']

export default function ClaudeBatchProcessingPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [prompts, setPrompts] = useState<string[]>([])
  const [batches, setBatches] = useState<BatchListResponse>({})
  const [showApiKey, setShowApiKey] = useState(false)
  const [anthropicApiKey, setAnthropicApiKey] = useState<string>('')

  const { toast } = useToast()
  const form = useForm<StartBatchProcessingRequest>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      prompt: '',
      chunk_size: 1000,
      chunk_by: 'word',
      selected_model: '',
      email: '',
      anthropic_api_key: '',
    },
  })

  useEffect(() => {
    fetchPrompts();
    fetchBatches();
    getUserConfig()
      .then((config) => {
        console.log("Fetched user config:", config);
        if (config) {
          // Update your local states
          setAnthropicApiKey(config.anthropic_api_key || "");
  
          // Also update the form fields
          if (config.anthropic_api_key) {
            form.setValue("anthropic_api_key", config.anthropic_api_key);
          }
        }
      })
      .catch((error) => {
        console.warn("User configuration not found or failed to retrieve.", error);
      });
  }, []);
  
  

  const fetchPrompts = async () => {
    console.log('fetchPrompts -> Called');
    try {
      const result = await listPrompts();
      console.log('fetchPrompts -> result:', result);

      // If result has a .prompts array, set that
      if (result && Array.isArray(result.prompts)) {
        setPrompts(result.prompts);
      }
      // If result is just an array, set that
      else if (Array.isArray(result)) {
        setPrompts(result);
      }
      // Otherwise, throw an error for unexpected structure
      else {
        throw new Error('Unexpected response structure');
      }
    } catch (err) {
      console.error('fetchPrompts -> error:', err);
      toast({
        title: 'Error',
        description: 'Failed to fetch prompts. Please try again.',
        variant: 'destructive',
      });
    }
  };

  const fetchBatches = async () => {
    setIsLoading(true)
    try {
      const response = await listClaudeBatches()
      if (response) {
        setBatches(response)
      }
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch batches. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'in_progress':
        return 'bg-[hsl(180,60%,50%)]' // Medium Teal (--secondary)
      case 'completed':
        return 'bg-[hsl(180,100%,25%)]' // Deep Teal (--primary)
      case 'failed':
        return 'bg-[hsl(0,100%,50%)]' // Red (--destructive)
      default:
        return 'bg-[hsl(180,20%,90%)]' // Light Muted Teal (--muted)
    }
  }

  const onSubmit = async (data: StartBatchProcessingRequest) => {
    setIsLoading(true)
    try {
      const response = await startClaudeBatchProcessing(data)
      if (response) {
        toast({
          title: "Batch Processing Started",
          description: `Batch ID: ${response.batch_id}`,
        })
        fetchBatches()
      }
    } catch {
      toast({
        title: "Error",
        description: "Failed to start batch processing. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefreshStatus = async (batchId: string) => {
    setIsLoading(true)
    try {
      const status = await getClaudeBatchStatus(batchId)
      if (status) {
        setBatches(prev => ({ ...prev, [batchId]: status }))
      }
    } catch {
      toast({
        title: "Error",
        description: "Failed to refresh batch status. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancelBatch = async (batchId: string) => {
    setIsLoading(true)
    try {
      const response = await cancelClaudeBatch(batchId)
      if (response) {
        toast({
          title: "Batch Cancelled",
          description: response.message,
        })
        fetchBatches()
      }
    } catch {
      toast({
        title: "Error",
        description: "Failed to cancel batch. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="container mx-auto py-10 space-y-8">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader className="bg-primary/10 rounded-t-lg">
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <Zap className="h-6 w-6" />
            Start Claude Batch Processing
          </CardTitle>
          <CardDescription>Configure and start a new batch processing task</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <SplitSquareVertical className="h-4 w-4" />
                      Prompt
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a prompt" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {prompts.map((prompt) => (
                          <SelectItem key={prompt} value={prompt}>{prompt}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="chunk_size"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Chunk Size</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value))}
                          placeholder="Enter chunk size"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="chunk_by"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Chunk By</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select chunking method" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="word">Word</SelectItem>
                          <SelectItem value="character">Character</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="selected_model"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Layers className="h-4 w-4" />
                      Model
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a model" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {modelOptions.map((model) => (
                          <SelectItem key={model} value={model}>{model}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      Email
                    </FormLabel>
                    <FormControl>
                      <Input {...field} type="email" placeholder="Enter your email" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="anthropic_api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Anthropic API Key</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input
                          {...field}
                          type={showApiKey ? "text" : "password"}
                          placeholder="Enter Anthropic API Key"
                          value={anthropicApiKey}
                          onChange={(e) => {
                            setAnthropicApiKey(e.target.value)
                            field.onChange(e.target.value)
                          }}
                          className="pr-10"
                        />
                        <button
                          type="button"
                          onClick={() => setShowApiKey(!showApiKey)}
                          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                          aria-label="Toggle API Key Visibility"
                        >
                          {showApiKey ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                        </button>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <Button type="submit" disabled={isLoading} className="w-full">
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                Start Batch Processing
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader className="bg-secondary/10 rounded-t-lg">
          <CardTitle className="text-xl font-semibold flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Batch Processing Tasks
          </CardTitle>
          <CardDescription>View and manage your batch processing tasks</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <ScrollArea className="h-[600px] pr-4">
            {Object.entries(batches).length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <AlertTriangle className="mx-auto h-12 w-12 mb-4" />
                <p>No batch processing tasks found.</p>
              </div>
            ) : (
              <Accordion type="single" collapsible className="space-y-4">
                {Object.entries(batches).map(([batchId, status]) => (
                  <AccordionItem key={batchId} value={batchId}>
                    <Card>
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <AccordionTrigger className="hover:no-underline">
                            <CardTitle className="text-lg flex items-center gap-2">
                              Batch ID: {batchId}
                            </CardTitle>
                          </AccordionTrigger>
                          <Badge className={getStatusColor(status.processing_status)}>
                            {status.processing_status}
                          </Badge>
                        </div>
                      </CardHeader>
                      <AccordionContent>
                        <CardContent className="pt-0">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4 text-gray-500" />
                              <span>Created: {status.created_at ? formatDate(status.created_at) : 'N/A'}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4 text-gray-500" />
                              <span>Ended: {status.ended_at ? formatDate(status.ended_at) : 'N/A'}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4 text-gray-500" />
                              <span>Expires: {formatDate(status.expires_at || '')}</span>
                            </div>
                            {status.results_url && (
                              <div className="flex items-center gap-2">
                                <Download className="h-4 w-4 text-blue-500" />
                                <a
                                  href={status.results_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-500 hover:underline"
                                >
                                  Download Results
                                </a>
                              </div>
                            )}
                          </div>
                          <div className="mt-4">
                            <h4 className="font-semibold mb-2">Request Counts:</h4>
                            <div className="grid grid-cols-2 gap-2">
                              {Object.entries(status.request_counts).map(([key, value]) => (
                                <div key={key} className="flex items-center justify-between bg-gray-100 p-2 rounded">
                                  <span className="font-medium">{key}:</span>
                                  <span>{value}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </CardContent>
                        <CardFooter className="flex justify-end space-x-2 pt-4">
                          <Button
                            onClick={() => handleRefreshStatus(batchId)}
                            variant="outline"
                            size="sm"
                            className="flex items-center gap-2"
                          >
                            <RefreshCw className="h-4 w-4" />
                            Refresh Status
                          </Button>
                          {status.processing_status.toLowerCase() === 'in_progress' && (
                            <Button
                              onClick={() => handleCancelBatch(batchId)}
                              variant="destructive"
                              size="sm"
                              className="flex items-center gap-2"
                            >
                              <XCircle className="h-4 w-4" />
                              Cancel Batch
                            </Button>
                          )}
                        </CardFooter>
                      </AccordionContent>
                    </Card>
                  </AccordionItem>
                ))}
              </Accordion>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  )
}