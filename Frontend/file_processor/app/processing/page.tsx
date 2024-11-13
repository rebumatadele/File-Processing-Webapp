'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Loader2, Play, RefreshCw, Eye, EyeOff } from 'lucide-react'; // Import Eye icons
import { startProcessing, getTaskStatus } from '@/api/processingUtils';
import { listPrompts } from '@/api/promptUtils';
import { ProcessingSettings, TaskStatusResponse } from '@/types/apiTypes';

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
  if (data.provider_choice === 'OpenAI') return !!data.openai_api_key;
  if (data.provider_choice === 'Anthropic') return !!data.anthropic_api_key;
  if (data.provider_choice === 'Gemini') return !!data.gemini_api_key;
  return true;
}, {
  message: 'API Key is required for the selected provider',
  path: ['api_key'],
});

const modelOptions = {
  OpenAI: ['gpt-3.5-turbo', 'gpt-4'],
  Anthropic: ['claude-3-5-sonnet-20240620', 'claude-3-5'],
  Gemini: ['gemini-1.5-flash', 'gemini-1.5'],
};

export default function ProcessingPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [prompts, setPrompts] = useState<string[]>([]);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null);
  const [showApiKey, setShowApiKey] = useState(false); // State to toggle API key visibility

  const { toast } = useToast();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      provider_choice: 'OpenAI',
      prompt: '',
      chunk_size: 1024,
      chunk_by: 'word',
      selected_model: '',
      email: '',
      openai_api_key: '',
      anthropic_api_key: '',
      gemini_api_key: '',
    },
  });

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      const promptList = await listPrompts();
      setPrompts(promptList);
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch prompts. Please try again.",
        variant: "destructive",
      });
    }
  };

  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    setIsLoading(true);
    try {
      // Prepare the payload with only the relevant API key
      const settings: ProcessingSettings = {
        provider_choice: data.provider_choice,
        prompt: data.prompt,
        chunk_size: data.chunk_size,
        chunk_by: data.chunk_by,
        selected_model: data.selected_model,
        email: data.email,
        openai_api_key: data.provider_choice === 'OpenAI' ? data.openai_api_key || '' : '',
        anthropic_api_key: data.provider_choice === 'Anthropic' ? data.anthropic_api_key || '' : '',
        gemini_api_key: data.provider_choice === 'Gemini' ? data.gemini_api_key || '' : '',
      };
      const response = await startProcessing(settings);
      setTaskId(response.task_id);
      toast({
        title: "Processing started",
        description: `Task ID: ${response.task_id}`,
      });
    } catch (error: unknown) {
      toast({
        title: "Error",
        description: (error as Error).message || "Failed to start processing. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const checkTaskStatus = async () => {
    if (!taskId) return;

    setIsLoading(true);
    try {
      const status = await getTaskStatus(taskId);
      setTaskStatus(status);
    } catch(error: unknown) {
      toast({
        title: "Error",
        description: (error as Error).message || "Failed to fetch task status. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const providerChoice = form.watch('provider_choice');

  return (
    <div className="container mx-auto py-10">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Start Processing</CardTitle>
          <CardDescription>Configure and start processing your files.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            {/* Remove the nested <form> and use the <Form> as the <form> element */}
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* AI Provider Selection */}
              <FormField
                control={form.control}
                name="provider_choice"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>AI Provider</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white border border-gray-300">
                          <SelectValue placeholder="Select an AI provider" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-white border border-gray-300">
                        <SelectItem value="OpenAI">OpenAI</SelectItem>
                        <SelectItem value="Anthropic">Anthropic</SelectItem>
                        <SelectItem value="Gemini">Gemini</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Model Selection */}
              <FormField
                control={form.control}
                name="selected_model"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Model</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white border border-gray-300">
                          <SelectValue placeholder="Select a model" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-white border border-gray-300">
                        {modelOptions[providerChoice]?.map((model) => (
                          <SelectItem key={model} value={model}>{model}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Prompt Selection */}
              <FormField
                control={form.control}
                name="prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Prompt</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white border border-gray-300">
                          <SelectValue placeholder="Select a prompt" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-white border border-gray-300">
                        {prompts.map((prompt) => (
                          <SelectItem key={prompt} value={prompt}>{prompt}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Chunk Size */}
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

              {/* Chunk By */}
              <FormField
                control={form.control}
                name="chunk_by"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Chunk By</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white border border-gray-300">
                          <SelectValue placeholder="Select chunking method" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-white border border-gray-300">
                        <SelectItem value="word">Word</SelectItem>
                        <SelectItem value="sentence">Sentence</SelectItem>
                        <SelectItem value="paragraph">Paragraph</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Email */}
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input {...field} type="email" placeholder="Enter your email" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* API Key */}
              <FormField
                control={form.control}
                name={
                  providerChoice === 'OpenAI' 
                    ? 'openai_api_key' 
                    : providerChoice === 'Anthropic' 
                      ? 'anthropic_api_key' 
                      : 'gemini_api_key'
                }
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      {providerChoice === 'OpenAI' && 'OpenAI API Key'}
                      {providerChoice === 'Anthropic' && 'Anthropic API Key'}
                      {providerChoice === 'Gemini' && 'Gemini API Key'}
                    </FormLabel>
                    <FormControl>
                      {/* Wrap Input and Button inside a single div */}
                      <div className="relative">
                        <Input
                          {...field}
                          type={showApiKey ? "text" : "password"}
                          placeholder={`Enter ${providerChoice} API Key`}
                          className="pr-10" // Add padding to accommodate the icon
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

              {/* Submit Button */}
              <Button type="submit" disabled={isLoading}>
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                Start Processing
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>

      {/* Task Status Card */}
      {taskId && (
        <Card className="max-w-4xl mx-auto mt-6">
          <CardHeader>
            <CardTitle>Task Status</CardTitle>
            <CardDescription>Check the status of your processing task.</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Task ID: {taskId}</p>
            {taskStatus && (
              <div className="mt-4">
                <p>Status: {taskStatus.status}</p>
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Button onClick={checkTaskStatus} disabled={isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
              Check Status
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}