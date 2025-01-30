"use client"

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { toast } from "@/hooks/use-toast"
import { Loader2, Upload, Trash2, Save, FileText, FolderOpen, Edit2 } from 'lucide-react'
import { listFiles, getFileContent, editFileContent, clearFiles, deleteFile } from '@/api/fileUtils'
import axiosInstance from '@/api/axiosInstance' // Make sure you have an axiosInstance
import { FileContentResponse } from '@/types/apiTypes'

// -- Crypto utility imports --
import { 
  readFileAsUint8Array, 
  generateRandomKey, 
  xorData, 
  toBase64 
} from '@/utils/cryptoUtils'

export default function FileManagementPage() {
  const [files, setFiles] = useState<File[]>([])
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [fileContent, setFileContent] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    fetchFiles()
  }, [])

  const fetchFiles = async () => {
    setIsLoading(true)
    try {
      const fileList = await listFiles()
      setUploadedFiles(fileList)
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch files. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFiles(Array.from(event.target.files))
    }
  }

  /**
   * Upload files with XOR encryption:
   * 1. Read each file as ArrayBuffer -> Uint8Array
   * 2. Generate random key (same length)
   * 3. XOR the file contents
   * 4. Convert XORed data & key to base64
   * 5. Send to server via FormData
   */
  const handleUpload = async () => {
    if (files.length === 0) return

    setIsLoading(true)
    try {
      const formData = new FormData()

      for (const file of files) {
        // 1) Read file into memory as bytes
        const fileBytes = await readFileAsUint8Array(file)

        // 2) Generate random key of the same length
        const randomKey = generateRandomKey(fileBytes.length)

        // 3) XOR to get encrypted bytes
        const encryptedBytes = xorData(fileBytes, randomKey)

        // 4) Convert both to base64
        const encryptedBase64 = toBase64(encryptedBytes)
        const keyBase64 = toBase64(randomKey)

        // 5) Append to FormData:
        //    - We'll send the filename as normal
        //    - The XORed data under 'encrypted_file'
        //    - The key under 'file_key'
        // You can choose any field names you want.
        formData.append('filename', file.name)
        formData.append('encrypted_file', encryptedBase64)
        formData.append('file_key', keyBase64)
      }

      // Post to your server endpoint (e.g., /files/upload)
      // Make sure your backend is expecting these FormData fields!
      await axiosInstance.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      toast({
        title: "Files uploaded",
        description: "Your files have been successfully uploaded (XOR-encrypted).",
      })

      // Refresh the file list
      await fetchFiles()
      setFiles([]) // reset
    } catch (error) {
      console.error("Upload error:", error)
      toast({
        title: "Error",
        description: "Failed to upload files. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectFile = async (filename: string) => {
    setIsLoading(true)
    try {
      const fileInfo: FileContentResponse = await getFileContent(filename)
      setSelectedFile(fileInfo.filename)
      setFileContent(fileInfo.content)
      setIsEditing(false)
    } catch (error) {
      console.error("Error fetching file content:", error)
      toast({
        title: "Error",
        description: "Failed to fetch file content. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveContent = async () => {
    if (!selectedFile) return

    setIsLoading(true)
    try {
      await editFileContent(selectedFile, fileContent)
      toast({
        title: "File updated",
        description: "Your changes have been saved successfully.",
      })
      setIsEditing(false)
    } catch {
      toast({
        title: "Error",
        description: "Failed to save changes. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearFiles = async () => {
    setIsLoading(true)
    try {
      await clearFiles()
      toast({
        title: "Files cleared",
        description: "All uploaded files have been removed.",
      })
      setUploadedFiles([])
      setSelectedFile(null)
      setFileContent('')
    } catch {
      toast({
        title: "Error",
        description: "Failed to clear files. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteFile = async (filename: string) => {
    const confirmDelete = window.confirm(`Are you sure you want to delete '${filename}'?`)
    if (!confirmDelete) return
  
    setIsLoading(true)
    try {
      const response = await deleteFile(filename)
      if ('message' in response) {
        toast({
          title: "File Deleted",
          description: response.message,
        })
        // Refresh the file list
        await fetchFiles()
  
        // If the deleted file was selected, clear the selection
        if (selectedFile === filename) {
          setSelectedFile(null)
          setFileContent('')
        }
      } else {
        toast({
          title: "Unexpected Response",
          description: "Received an unexpected response from the server.",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error deleting file:", error)
      toast({
        title: "Error",
        description: `Failed to delete file '${filename}'. Please try again.`,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader className="bg-primary/10 rounded-t-lg">
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <FolderOpen className="h-6 w-6 text-primary" />
            File Management
          </CardTitle>
          <CardDescription>Upload, view, edit, and manage your files.</CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <Card className="bg-secondary/5">
            <CardContent className="p-4">
              <div className="flex items-center space-x-4">
                <Input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="flex-grow"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleUpload}
                  disabled={files.length === 0 || isLoading}
                  className="min-w-[100px]"
                >
                  {isLoading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="mr-2 h-4 w-4" />
                  )}
                  Upload
                </Button>
              </div>
            </CardContent>
          </Card>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="h-[400px] flex flex-col">
              <CardHeader className="bg-muted/50">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  Uploaded Files
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-grow overflow-hidden p-0">
                <ScrollArea className="h-full p-4">
                  {uploadedFiles.length === 0 ? (
                    <p className="text-muted-foreground text-center py-4">No files uploaded yet.</p>
                  ) : (
                    uploadedFiles.map((file) => (
                      <div key={file} className="flex items-center justify-between mb-2">
                        <Button
                          variant="ghost"
                          className="flex-grow justify-start"
                          onClick={() => handleSelectFile(file)}
                          disabled={isLoading}
                        >
                          <FileText className="mr-2 h-4 w-4" />
                          {file}
                        </Button>
                        <Button
                          variant="destructive"
                          size="icon"
                          onClick={() => handleDeleteFile(file)}
                          disabled={isLoading}
                          className="ml-2"
                          aria-label={`Delete ${file}`}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
            <Card className="h-[400px] flex flex-col">
              <CardHeader className="bg-muted/50">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  File Content
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-grow p-4 flex flex-col">
                <Textarea
                  value={fileContent}
                  onChange={(e) => setFileContent(e.target.value)}
                  disabled={!isEditing || isLoading}
                  className="flex-grow resize-none"
                  placeholder={selectedFile ? "Loading content..." : "Select a file to view its content"}
                />
              </CardContent>
              <CardFooter className="bg-muted/30 rounded-b-lg flex justify-end space-x-2 p-2">
                {selectedFile && (
                  <>
                    {isEditing ? (
                      <Button onClick={handleSaveContent} disabled={isLoading}>
                        {isLoading ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <Save className="mr-2 h-4 w-4" />
                        )}
                        Save
                      </Button>
                    ) : (
                      <Button onClick={() => setIsEditing(true)} disabled={isLoading}>
                        <Edit2 className="mr-2 h-4 w-4" />
                        Edit
                      </Button>
                    )}
                  </>
                )}
              </CardFooter>
            </Card>
          </div>
        </CardContent>
        <CardFooter className="bg-muted/10 rounded-b-lg flex justify-between p-4">
          <Button variant="destructive" onClick={handleClearFiles} disabled={isLoading}>
            {isLoading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="mr-2 h-4 w-4" />
            )}
            Clear All Files
          </Button>
          <Button onClick={() => (window.location.href = "/processing")}>
            Next
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
