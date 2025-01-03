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
import { Loader2, Play, RefreshCw, Eye, EyeOff, Cpu, Zap, Mail, Layers, SplitSquareVertical } from 'lucide-react'
import { startProcessing, getTaskStatus } from '@/api/processingUtils'
import { listPrompts } from '@/api/promptUtils'
import { ProcessingSettings, TaskStatusResponse } from '@/types/apiTypes'
import { getUserConfig } from '@/api/configUtils'

const formSchema = z.object({
  provider_choice: z.enum(['OpenAI', 'Anthropic', 'Gemini']),
  prompt: z.string().min(1, 'Please select a prompt'),
  chunk_size: z.number().int().positive().min(1, 'Chunk size must be a positive integer'),
  chunk_by: z.enum(['word', 'sentence', 'paragraph']),
  selected_model: z.string().min(1, 'Please select a model'),
  email: z.string().email('Please enter a valid email address'),
  openai_api_key: z.string().optional(),
  anthropic_api_key: z.string().optional(),
  gemini_api_key: z.string().optional(),
}).refine((data) => {
  if (data.provider_choice === 'OpenAI') return !!data.openai_api_key
  if (data.provider_choice === 'Anthropic') return !!data.anthropic_api_key
  if (data.provider_choice === 'Gemini') return !!data.gemini_api_key
  return true
}, {
  message: 'API Key is required for the selected provider',
  path: ['api_key'],
})

const modelOptions = {
  OpenAI: ['gpt-3.5-turbo', 'gpt-4'],
  Anthropic: ['claude-3-5-sonnet-20240620', 'claude-3-5'],
  Gemini: ['gemini-1.5-flash', 'gemini-1.5'],
}

export default function ProcessingPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [prompts, setPrompts] = useState<string[]>([])
  const [taskId, setTaskId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [openaiApiKey, setOpenaiApiKey] = useState<string>('')
  const [anthropicApiKey, setAnthropicApiKey] = useState<string>('')
  const [geminiApiKey, setGeminiApiKey] = useState<string>('')

  const { toast } = useToast()
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      provider_choice: 'Gemini',
      prompt: '',
      chunk_size: 200,
      chunk_by: 'word',
      selected_model: '',
      email: '',
      openai_api_key: '',
      anthropic_api_key: '',
      gemini_api_key: '',
    },
  })

  const providerChoice = form.watch('provider_choice')
  
  useEffect(() => {
    fetchPrompts()
    getUserConfig("1").then((config) => {
      if (config) {
        setOpenaiApiKey(config.openai_api_key || '')
      }
    })
    getUserConfig("2").then((config) => {
      if (config) {
        setGeminiApiKey(config.gemini_api_key || '')
      }
    })
    getUserConfig("3").then((config) => {
      if (config) {
        setAnthropicApiKey(config.anthropic_api_key || '')
      }
    })
  }, [])

  const fetchPrompts = async () => {
    try {
      const promptList = await listPrompts()
      setPrompts(promptList)
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch prompts. Please try again.",
        variant: "destructive",
      })
    }
  }

  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    setIsLoading(true)
    try {
      let apiKey = ''
      if (data.provider_choice === 'OpenAI') {
        apiKey = openaiApiKey
      } else if (data.provider_choice === 'Anthropic') {
        apiKey = anthropicApiKey
      } else if (data.provider_choice === 'Gemini') {
        apiKey = geminiApiKey
      }

      const settings: ProcessingSettings = {
        provider_choice: data.provider_choice,
        prompt: data.prompt,
        chunk_size: data.chunk_size,
        chunk_by: data.chunk_by,
        selected_model: data.selected_model,
        email: data.email,
        openai_api_key: data.provider_choice === 'OpenAI' ? apiKey : '',
        anthropic_api_key: data.provider_choice === 'Anthropic' ? apiKey : '',
        gemini_api_key: data.provider_choice === 'Gemini' ? apiKey : '',
      }

      const response = await startProcessing(settings)
      setTaskId(response.task_id)
      toast({
        title: "Processing started",
        description: `Task ID: ${response.task_id}`,
      })
    } catch (error: unknown) {
      toast({
        title: "Error",
        description: (error as Error).message || "Failed to start processing. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const checkTaskStatus = async () => {
    if (!taskId) return

    setIsLoading(true)
    try {
      const status = await getTaskStatus(taskId)
      setTaskStatus(status)
    } catch(error: unknown) {
      toast({
        title: "Error",
        description: (error as Error).message || "Failed to fetch task status. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-10 space-y-8">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader className="bg-primary/10 rounded-t-lg">
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <Zap className="h-6 w-6" />
            Start Processing
          </CardTitle>
          <CardDescription>Configure and start processing your files.</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <FormField
                  control={form.control}
                  name="provider_choice"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="flex items-center gap-2">
                        <Cpu className="h-4 w-4" />
                        AI Provider
                      </FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select an AI provider" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="OpenAI">OpenAI</SelectItem>
                          <SelectItem value="Anthropic">Anthropic</SelectItem>
                          <SelectItem value="Gemini">Gemini</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

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
                          {modelOptions[providerChoice]?.map((model) => (
                            <SelectItem key={model} value={model}>{model}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

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
                          <SelectItem value="sentence">Sentence</SelectItem>
                          <SelectItem value="paragraph">Paragraph</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

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

              {providerChoice === 'OpenAI' && (
                <FormField
                  control={form.control}
                  name="openai_api_key"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>OpenAI API Key</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            {...field}
                            type={showApiKey ? "text" : "password"}
                            placeholder="Enter OpenAI API Key"
                            value={openaiApiKey}
                            onChange={(e) => {
                              setOpenaiApiKey(e.target.value)
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
              )}

              {providerChoice === 'Anthropic' && (
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
              )}

              {providerChoice === 'Gemini' && (
                <FormField
                  control={form.control}
                  name="gemini_api_key"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Gemini API Key</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            {...field}
                            type={showApiKey ? "text" : "password"}
                            placeholder="Enter Gemini API Key"
                            value={geminiApiKey}
                            onChange={(e) => {
                              setGeminiApiKey(e.target.value)
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
              )}

              <Button type="submit" disabled={isLoading} className="w-full">
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                Start Processing
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {taskId && (
        <Card className="w-full max-w-4xl mx-auto">
          <CardHeader className="bg-secondary/10 rounded-t-lg">
            <CardTitle className="text-xl font-semibold flex items-center gap-2">
              <RefreshCw className="h-5 w-5" />
              Task Status
            </CardTitle>
            <CardDescription>Check the status of your processing task.</CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <p className="text-lg font-medium">Task ID: <span className="text-primary">{taskId}</span></p>
            {taskStatus && (
              <div className="mt-4">
                <p className="text-lg">Status: <span className="font-semibold text-secondary">{taskStatus.status}</span></p>
              </div>
            )}
          </CardContent>
          <CardFooter className="bg-secondary/5 rounded-b-lg">
            <Button onClick={checkTaskStatus} disabled={isLoading} className="w-full">
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
              Check Status
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}