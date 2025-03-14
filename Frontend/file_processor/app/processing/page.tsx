"use client"

import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from "@/components/ui/card"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { useToast } from "@/hooks/use-toast"
import {
  Loader2,
  Play,
  RefreshCw,
  Eye,
  EyeOff,
  Cpu,
  Zap,
  Mail,
  Layers,
  SplitSquareVertical,
  Files
} from "lucide-react"
import {
  startProcessing,
  getTaskStatus,
  getProcessingProgress
} from "@/api/processingUtils"
import { listFiles } from "@/api/fileUtils"
import { listPrompts, loadPrompt } from "@/api/promptUtils"
import { getUserConfig } from "@/api/configUtils"
import {
  ProcessingSettings,
  TaskStatusResponse,
  StartProcessingResponse,
  GetProcessingProgressResponse
} from "@/types/apiTypes"

/** Zod Schema */
const formSchema = z.object({
  provider_choice: z.enum(["OpenAI", "Anthropic", "Gemini"]),
  prompt: z.string().min(1, "Please select a prompt"),
  chunk_size: z.number().int().positive().min(1, "Chunk size must be a positive integer"),
  chunk_by: z.enum(["word", "sentence", "paragraph"]),
  selected_model: z.string().min(1, "Please select a model"),
  email: z.string().email("Please enter a valid email address"),
  openai_api_key: z.string().optional(),
  anthropic_api_key: z.string().optional(),
  gemini_api_key: z.string().optional(),
  // Required array of file strings:
  selected_files: z.array(z.string()).min(1, "Please select at least one file")
}).refine((data) => {
  // Provider-specific API key requirement
  if (data.provider_choice === "OpenAI") return !!data.openai_api_key
  if (data.provider_choice === "Anthropic") return !!data.anthropic_api_key
  if (data.provider_choice === "Gemini") return !!data.gemini_api_key
  return true
}, {
  message: "API Key is required for the selected provider",
  path: ["api_key"]
})

const modelOptions = {
  OpenAI: ["gpt-3.5-turbo", "gpt-4"],
  Anthropic: ["claude-3-5-sonnet-20240620", "claude-3-5"],
  Gemini: ["gemini-1.5-flash", "gemini-1.5"]
}

export default function ProcessingPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [prompts, setPrompts] = useState<string[]>([])
  const [taskId, setTaskId] = useState<string | null>(null)
  const [jobId, setJobId] = useState<string | null>(null)
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null)
  const [jobProgress, setJobProgress] = useState<GetProcessingProgressResponse | null>(null)
  const [showApiKey, setShowApiKey] = useState(false)
  const [openaiApiKey, setOpenaiApiKey] = useState<string>("")
  const [anthropicApiKey, setAnthropicApiKey] = useState<string>("")
  const [geminiApiKey, setGeminiApiKey] = useState<string>("")
  const [files, setFiles] = useState<string[]>([])

  const { toast } = useToast()

  /** React Hook Form Setup */
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      provider_choice: "Gemini",
      prompt: "",
      chunk_size: 200,
      chunk_by: "word",
      selected_model: "",
      email: "",
      openai_api_key: "",
      anthropic_api_key: "",
      gemini_api_key: "",
      selected_files: []
    }
  })

  /** Watch the current provider choice for conditional rendering */
  const providerChoice = form.watch("provider_choice")

  /** On Mount: fetch prompts, files, and retrieve any task/job IDs from localStorage */
  useEffect(() => {
    fetchPrompts()
    fetchFiles()

    const storedTaskId = localStorage.getItem("taskId")
    const storedJobId = localStorage.getItem("jobId")

    if (storedTaskId && storedJobId) {
      setTaskId(storedTaskId)
      setJobId(storedJobId)
      checkTaskStatus(storedTaskId, storedJobId)
    }

    getUserConfig()
      .then((config) => {
        if (config) {
          setOpenaiApiKey(config.openai_api_key || "")
          setGeminiApiKey(config.gemini_api_key || "")
          setAnthropicApiKey(config.anthropic_api_key || "")

          // Update RHF form fields
          if (config.openai_api_key) form.setValue("openai_api_key", config.openai_api_key)
          if (config.anthropic_api_key) form.setValue("anthropic_api_key", config.anthropic_api_key)
          if (config.gemini_api_key) form.setValue("gemini_api_key", config.gemini_api_key)
        }
      })
      .catch((error) => {
        console.warn("User configuration not found or failed to retrieve.", error)
      })
  }, [])

  /** Fetch the list of prompts from the backend */
  const fetchPrompts = async () => {
    try {
      const result = await listPrompts()
      // Some servers return { prompts: string[] }, some just return string[]
      if (result && Array.isArray(result.prompts)) {
        setPrompts(result.prompts)
      } else if (Array.isArray(result)) {
        setPrompts(result)
      } else {
        throw new Error("Unexpected prompt response structure")
      }
    } catch (err) {
      console.error("fetchPrompts -> error:", err)
      toast({
        title: "Error",
        description: "Failed to fetch prompts. Please try again.",
        variant: "destructive"
      })
    }
  }

  /** Fetch the list of files from the backend */
  const fetchFiles = async () => {
    try {
      const fileList = await listFiles()
      setFiles(fileList)
    } catch (err) {
      console.error("Error fetching files:", err)
      toast({
        title: "Error",
        description: "Failed to fetch files. Please try again.",
        variant: "destructive"
      })
    }
  }

  /**
   * Called when user clicks "Start Processing" and the form is valid.
   */
  const onSubmit = async (data: z.infer<typeof formSchema>) => {
    setIsLoading(true)
    try {
      let apiKey = ""
      if (data.provider_choice === "OpenAI") apiKey = openaiApiKey
      else if (data.provider_choice === "Anthropic") apiKey = anthropicApiKey
      else if (data.provider_choice === "Gemini") apiKey = geminiApiKey

      const promptContent = await loadPrompt(data.prompt)
      const settings: ProcessingSettings = {
        provider_choice: data.provider_choice,
        prompt: promptContent.content,
        chunk_size: data.chunk_size,
        chunk_by: data.chunk_by,
        selected_model: data.selected_model,
        email: data.email,
        openai_api_key: data.provider_choice === "OpenAI" ? apiKey : "",
        anthropic_api_key: data.provider_choice === "Anthropic" ? apiKey : "",
        gemini_api_key: data.provider_choice === "Gemini" ? apiKey : "",
        files: data.selected_files
      }

      const response: StartProcessingResponse = await startProcessing(settings)
      setTaskId(response.task_id)
      setJobId(response.job_id)

      localStorage.setItem("taskId", response.task_id)
      localStorage.setItem("jobId", response.job_id)

      toast({
        title: "Processing started",
        description: `Task ID: ${response.task_id}, Job ID: ${response.job_id}`
      })
    } catch (error: unknown) {
      console.error("onSubmit -> Error starting processing:", error)
      toast({
        title: "Error",
        description:
          (error as Error).message || "Failed to start processing. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  /**
   * Checks the task status and job progress for the current Task/Job IDs.
   */
  const checkTaskStatus = async (currentTaskId?: string, currentJobId?: string) => {
    const id = currentTaskId || taskId
    const jId = currentJobId || jobId
    if (!id || !jId) return

    setIsLoading(true)
    try {
      const status: TaskStatusResponse = await getTaskStatus(id)
      setTaskStatus(status)

      if (status.job_id) {
        setJobId(status.job_id)
        const progress: GetProcessingProgressResponse = await getProcessingProgress(status.job_id)
        setJobProgress(progress)
      }

      // Clear IDs from storage if completed
      if (status.status === "Completed") {
        localStorage.removeItem("taskId")
        localStorage.removeItem("jobId")
      }
    } catch (error: unknown) {
      const errMessage = (error as Error).message || ""
      console.error("checkTaskStatus -> Error:", error)

      // If we get "Task ID not found," assume the server has pruned it => "Completed"
      if (errMessage.includes("Task ID not found")) {
        toast({
          title: "Task Completed",
          description: "Server indicates the task no longer exists. Marking as completed."
        })
        localStorage.removeItem("taskId")
        localStorage.removeItem("jobId")
        setTaskId(null)
        setJobId(null)
        setTaskStatus(null)
        setJobProgress(null)
      } else {
        toast({
          title: "Error",
          description: errMessage || "Failed to fetch task status. Please try again.",
          variant: "destructive"
        })
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Determine file selection states:
  const selectedFiles = form.watch("selected_files")
  const allFilesSelected = selectedFiles.length === files.length && files.length > 0
  const someFilesSelected = selectedFiles.length > 0 && selectedFiles.length < files.length

  // For the single "Select All" checkbox, we pass a union type to "checked":
  //  - true if all are selected
  //  - "indeterminate" if only some
  //  - false if none
  let selectAllValue: boolean | "indeterminate" = false
  if (allFilesSelected) {
    selectAllValue = true
  } else if (someFilesSelected) {
    selectAllValue = "indeterminate"
  }

  return (
    <div className="container mx-auto py-10 space-y-8">
      {/* Processing Form */}
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
            <div className="space-y-6">
              {/* Provider Choice + Model */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* AI Provider */}
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
                {/* Model */}
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
                            <SelectItem key={model} value={model}>
                              {model}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              {/* Prompt */}
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
                          <SelectItem key={prompt} value={prompt}>
                            {prompt}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* File Selection: Single "Select All" toggle + file list */}
              <FormField
                control={form.control}
                name="selected_files"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center gap-2">
                      <Files className="h-4 w-4" />
                      Select Files
                    </FormLabel>
                    <FormControl>
                      <div className="border rounded p-2 max-h-60 overflow-y-auto">
                        {/* One checkbox to select/deselect all */}
                        <div className="flex items-center mb-4">
                          <Checkbox
                            // For Radix-based Checkbox from shadcn/ui:
                            // - boolean | "indeterminate" is allowed for "checked"
                            checked={selectAllValue}
                            onCheckedChange={(checked) => {
                              if (checked === true) {
                                // If user toggles to checked, select all
                                field.onChange(files)
                              } else {
                                // If user toggles to unchecked or "indeterminate" => deselect all
                                field.onChange([])
                              }
                            }}
                            id="select-all-toggle"
                          />
                          <label
                            htmlFor="select-all-toggle"
                            className="text-sm font-medium leading-none ml-2"
                          >
                            Select All
                          </label>
                        </div>

                        {/* Individual file checkboxes */}
                        {files.length === 0 ? (
                          <div className="text-sm text-muted-foreground">Loading files...</div>
                        ) : (
                          files.map((file) => {
                            const isChecked = field.value?.includes(file)
                            return (
                              <div key={file} className="flex items-center space-x-2 mb-2">
                                <Checkbox
                                  id={file}
                                  // For each item, boolean for checked
                                  checked={!!isChecked}
                                  onCheckedChange={() => {
                                    const updatedFiles = isChecked
                                      ? field.value.filter((f) => f !== file)
                                      : [...field.value, file]
                                    field.onChange(updatedFiles)
                                  }}
                                />
                                <label
                                  htmlFor={file}
                                  className="text-sm font-medium leading-none"
                                >
                                  {file}
                                </label>
                              </div>
                            )
                          })
                        )}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* Chunk Size + Chunk By */}
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

              {/* Email */}
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

              {/* Conditional API Key Fields */}
              {providerChoice === "OpenAI" && (
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
                            type={showApiKey ? "text" : "text"} // Simplified to text
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

              {providerChoice === "Anthropic" && (
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
                            type={showApiKey ? "text" : "text"}
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

              {providerChoice === "Gemini" && (
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
                            type={showApiKey ? "text" : "text"}
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

              {/* Start Processing Button */}
              <Button
                onClick={() => {
                  form.handleSubmit(
                    (data) => onSubmit(data),
                    (errors) => {
                      console.log("Invalid data callback called with errors:", errors)
                    }
                  )()
                }}
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Play className="mr-2 h-4 w-4" />
                )}
                Start Processing
              </Button>
            </div>
          </Form>
        </CardContent>
      </Card>

      {/* Task Status Section */}
      {taskId && jobId && (
        <Card className="w-full max-w-4xl mx-auto">
          <CardHeader className="bg-secondary/10 rounded-t-lg">
            <CardTitle className="text-xl font-semibold flex items-center gap-2">
              <RefreshCw className="h-5 w-5" />
              Task & Job Status
            </CardTitle>
            <CardDescription>Check the status of your processing task and job.</CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <div className="space-y-4">
              <p className="text-lg font-medium">
                Task ID: <span className="text-primary">{taskId}</span>
              </p>
              <p className="text-lg font-medium">
                Job ID: <span className="text-secondary">{jobId}</span>
              </p>
              <p className="text-lg">
                Status:{" "}
                <span className="font-semibold text-secondary">
                  {taskStatus?.status || "Loading..."}
                </span>
              </p>
            </div>

            {/* Detailed Job Progress */}
            {jobProgress && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-2">Detailed Progress</h3>
                <div className="space-y-4">
                  {jobProgress.files.map((fileStatus) => (
                    <Card key={fileStatus.filename} className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium">{fileStatus.filename}</span>
                        <span
                          className={`text-sm font-semibold ${
                            fileStatus.status === "Completed"
                              ? "text-green-600"
                              : "text-yellow-600"
                          }`}
                        >
                          {fileStatus.status}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                        <div
                          className={`bg-${
                            fileStatus.status === "Completed" ? "green" : "yellow"
                          }-500 h-2.5 rounded-full`}
                          style={{ width: `${fileStatus.progress_percentage}%` }}
                        />
                      </div>
                      <p className="text-sm text-gray-600">
                        {fileStatus.processed_chunks} / {fileStatus.total_chunks} chunks processed
                      </p>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
          <CardFooter className="bg-secondary/5 rounded-b-lg flex justify-between">
            <Button onClick={() => checkTaskStatus()} disabled={isLoading} className="w-full">
              {isLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="mr-2 h-4 w-4" />
              )}
              Refresh Status
            </Button>
            <Button
              onClick={() => (window.location.href = "/results")}
              disabled={jobProgress?.job_status !== "Completed"}
              className="ml-4"
            >
              Next
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}
