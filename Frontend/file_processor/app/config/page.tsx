'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Eye, EyeOff, Settings, Cpu, Key } from 'lucide-react'
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { configureProvider, getUserConfig } from '../../api/configUtils'
import { ConfigRequest } from '@/types/apiTypes'

const formSchema = z.object({
  selected_model: z.string().min(1, 'Please select a model'),
  provider_choice: z.enum(['OpenAI', 'Gemini', 'Anthropic']),
  api_key: z.string().min(1, 'API Key is required')
}).refine((data) => {
  if (data.provider_choice === 'OpenAI' || data.provider_choice === 'Anthropic') {
    return data.api_key.startsWith('sk-');
  }
  return true;
}, {
  message: 'API Key must start with "sk-" for OpenAI and Anthropic',
  path: ['api_key'],
});

type FormValues = z.infer<typeof formSchema>

const modelOptions = {
  OpenAI: ['gpt-3.5-turbo', 'gpt-4'],
  Gemini: ['gemini-1.5-flash', 'gemini-1.5'],
  Anthropic: ['claude-3-5-sonnet-20240620', 'claude-3-5'],
}

export default function ConfigurationPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const { toast } = useToast()
  const [isConfigSaved, setIsConfigSaved] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      selected_model: '',
      provider_choice: 'Gemini',
      api_key: '',
    },
  })

  useEffect(() => {
    const loadUserConfig = async () => {
      try {
        const config = await getUserConfig();
  
        if (config) {
          // Populate form based on retrieved configuration
          if (config.gemini_api_key) {
            form.setValue('provider_choice', 'Gemini');
            form.setValue('api_key', config.gemini_api_key || '');
            form.setValue('selected_model', modelOptions.Gemini[0]);
          } else if (config.anthropic_api_key) {
            form.setValue('provider_choice', 'Anthropic');
            form.setValue('api_key', config.anthropic_api_key || '');
            form.setValue('selected_model', modelOptions.Anthropic[0]);
          } else if (config.openai_api_key) {
            form.setValue('provider_choice', 'OpenAI');
            form.setValue('api_key', config.openai_api_key || '');
            form.setValue('selected_model', modelOptions.OpenAI[0]);
          } else {
            toast({
              title: "Configuration Not Found",
              description: "No configuration found for your account. Please set up your preferences.",
              variant: "destructive",
            });
          }
        } else {
          toast({
            title: "Configuration Not Found",
            description: "No configuration found for your account. Please set up your preferences.",
            variant: "destructive",
          });
        }
      } catch (error) {
        toast({
          title: "Error Loading Configuration",
          description:
            error instanceof Error
              ? error.message
              : "An unexpected error occurred while loading your configuration. Please try again.",
          variant: "destructive",
        });
      }
    };
  
    loadUserConfig();
    // Removed toast from dependency array
  }, [form]);

  const onSubmit = async (data: FormValues) => {
    setIsLoading(true)
    setIsConfigSaved(true);

    try {
      const configRequest: ConfigRequest = {
        provider_choice: data.provider_choice,
        selected_model: data.selected_model,
        api_key: data.api_key,
      }

      await configureProvider(configRequest)

      toast({
        title: "Configuration saved",
        description: "Your AI model preferences have been updated.",
      })
    } catch (error: unknown) {
      toast({
        title: "Error",
        description: (error instanceof Error ? error.message : "Failed to save configuration. Please try again."),
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="max-w-2xl mx-auto">
        <CardHeader className="bg-primary/10 rounded-t-lg">
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <Settings className="h-6 w-6 text-primary" />
            AI Model Configuration
          </CardTitle>
          <CardDescription>Set up your AI model preferences for file processing.</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              {/* Provider Choice Field */}
              <FormField
                control={form.control}
                name="provider_choice"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-primary" />
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
                        <SelectItem value="Gemini">Gemini</SelectItem>
                        <SelectItem value="Anthropic">Anthropic</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Choose your preferred AI service provider.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Model Selection Field */}
              <FormField
                control={form.control}
                name="selected_model"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Cpu className="h-4 w-4 text-primary" />
                      Model
                    </FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select a model" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {modelOptions[form.watch('provider_choice')].map((model) => (
                          <SelectItem key={model} value={model}>{model}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormDescription>
                      Select the AI model you want to use for processing.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* API Key Field */}
              <FormField
                control={form.control}
                name="api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Key className="h-4 w-4 text-primary" />
                      API Key
                    </FormLabel>
                    <div className="relative">
                      <FormControl>
                        <Input
                          placeholder="Enter your API key"
                          {...field}
                          type={showApiKey ? "text" : "text"}
                          className="pr-10"
                        />
                      </FormControl>
                      <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 focus:outline-none"
                        aria-label={showApiKey ? "Hide API Key" : "Show API Key"}
                      >
                        {showApiKey ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                      </button>
                    </div>
                    <FormDescription>
                      Enter your API key for the selected provider. For OpenAI and Anthropic, it should start with <code className="bg-muted px-1 py-0.5 rounded">sk-</code>.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </form>
          </Form>
        </CardContent>
        <CardFooter className="bg-muted/10 rounded-b-lg flex justify-between">
          <Button 
            onClick={form.handleSubmit(onSubmit)} 
            className="w-full mr-2" 
            disabled={isLoading}
          >
            {isLoading ? "Saving..." : "Save Configuration"}
          </Button>
          <Button 
            onClick={() => window.location.href = "/prompt-management"} 
            className="w-full ml-2"
            disabled={!isConfigSaved}
          >
            Next
          </Button>
        </CardFooter>

      </Card>
    </div>
  )
}
