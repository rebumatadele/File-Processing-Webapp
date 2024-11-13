'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Eye, EyeOff } from 'lucide-react'
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { configureProvider } from '../../api/configUtils'

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
  path: ['api_key'], // this specifies that the error is on the api_key field
});


type FormValues = z.infer<typeof formSchema>

export default function ConfigurationPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [showApiKey, setShowApiKey] = useState(false)
  const { toast } = useToast()

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      selected_model: 'gemini-1.5-flash',
      provider_choice: 'Gemini',
      api_key: 'AIzaSyARFySyhjCOD4VLh0r6TB_EOy1CTTk7TaA',
    },
  })

  const onSubmit = async (data: FormValues) => {
    setIsLoading(true)
    try {
      await configureProvider({
        provider_choice: data.provider_choice,
        selected_model: data.selected_model,
        api_key: data.api_key,
      })
      toast({
        title: "Configuration saved",
        description: "Your AI model preferences have been updated.",
      })
    } catch{
      toast({
        title: "Error",
        description: "Failed to save configuration. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const modelOptions = {
    OpenAI: ['gpt-3.5-turbo', 'gpt-4'],
    Gemini: ['gemini-1.5-flash', 'gemini-1.5'],
    Anthropic: ['claude-3-5-sonnet-20240620', 'claude-3-5'],
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>AI Model Configuration</CardTitle>
          <CardDescription>Set up your AI model preferences for file processing.</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <FormField
                control={form.control}
                name="provider_choice"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>AI Provider</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white text-black border border-gray-300">
                          <SelectValue placeholder="Select an AI provider" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-white">
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
              <FormField
                control={form.control}
                name="selected_model"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Model</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white text-black border border-gray-300">
                          <SelectValue placeholder="Select a model" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent className="bg-white">
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
              <FormField
                control={form.control}
                name="api_key"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>API Key</FormLabel>
                    <div className="relative">
                      <FormControl>
                        <Input
                          placeholder="Enter your API key"
                          {...field}
                          type={showApiKey ? "text" : "password"}
                        />
                      </FormControl>
                      <button
                        type="button"
                        onClick={() => setShowApiKey(!showApiKey)}
                        className="absolute right-2 top-2"
                      >
                        {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    <FormDescription>
                      Enter your API key for the selected provider. For OpenAI and Anthropic, it should start with sk-.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Saving..." : "Save Configuration"}
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
