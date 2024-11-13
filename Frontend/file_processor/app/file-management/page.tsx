'use client'

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "@/hooks/use-toast"
import { Loader2, Upload, Trash2, Save, FileText } from 'lucide-react'
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
    } catch{
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
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>File Management</CardTitle>
          <CardDescription>Upload, view, edit, and manage your files.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center space-x-4">
            <Input type="file" multiple onChange={handleFileChange} />
            <Button onClick={handleUpload} disabled={files.length === 0 || isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
              Upload
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Uploaded Files</CardTitle>
              </CardHeader>
              <CardContent className="h-[300px] overflow-y-auto">
                {uploadedFiles.map((file) => (
                  <Button
                    key={file}
                    variant="ghost"
                    className="w-full justify-start"
                    onClick={() => handleSelectFile(file)}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    {file}
                  </Button>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>File Content</CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={fileContent}
                  onChange={(e) => setFileContent(e.target.value)}
                  disabled={!isEditing || isLoading}
                  className="h-[200px]"
                  placeholder={selectedFile ? "Loading content..." : "Select a file to view its content"}
                />
              </CardContent>
              <CardFooter className="flex justify-end space-x-2">
                {selectedFile && (
                  <>
                    {isEditing ? (
                      <Button onClick={handleSaveContent} disabled={isLoading}>
                        {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                        Save
                      </Button>
                    ) : (
                      <Button onClick={() => setIsEditing(true)} disabled={isLoading}>
                        Edit
                      </Button>
                    )}
                  </>
                )}
              </CardFooter>
            </Card>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="destructive" onClick={handleClearFiles} disabled={isLoading}>
            {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Trash2 className="mr-2 h-4 w-4" />}
            Clear All Files
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}