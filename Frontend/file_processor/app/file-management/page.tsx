'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { toast } from "@/hooks/use-toast"
import { Loader2, Upload, Trash2, Save, FileText, FolderOpen, Edit2 } from 'lucide-react'
import { uploadFiles, listFiles, getFileContent, editFileContent, clearFiles } from '@/api/fileUtils'
import { UploadedFileInfo } from '@/types/apiTypes'

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

  const handleUpload = async () => {
    setIsLoading(true)
    try {
      await uploadFiles(files)
      toast({
        title: "Files uploaded",
        description: "Your files have been successfully uploaded.",
      })
      fetchFiles()
      setFiles([])
    } catch {
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
      const fileInfo: UploadedFileInfo = await getFileContent(filename)
      setSelectedFile(filename)
      setFileContent(fileInfo.content)
      setIsEditing(false)
    } catch {
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
                      <Button
                        key={file}
                        variant="ghost"
                        className="w-full justify-start mb-2"
                        onClick={() => handleSelectFile(file)}
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        {file}
                      </Button>
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
        </CardFooter>
      </Card>
    </div>
  )
}