'use client'

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useToast } from "@/hooks/use-toast"
import { Trash2, Plus, Save, Edit2, FileText, List } from 'lucide-react'
import { listPrompts, loadPrompt, savePrompt, deletePrompt } from '../../api/promptUtils'

type Prompt = {
  id: string
  name: string
  content: string
}

export default function PromptManagementPage() {
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const { toast } = useToast()

  useEffect(() => {
    fetchPrompts()
  }, [])

  const fetchPrompts = async () => {
    setIsLoading(true);
    try {
      // Destructure the response to get the list of prompt names
      const { prompts: promptNames } = await listPrompts();

      const fetchedPrompts = await Promise.all(
        promptNames.map(async (name: string) => {
          const prompt = await loadPrompt(name);
          return { ...prompt, id: name };
        })
      );
      setPrompts(fetchedPrompts);
    } catch {
      toast({
        title: "Error",
        description: "Failed to fetch prompts.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }

  const handleSelectPrompt = async (promptId: string) => {
    setIsLoading(true)
    const prompt = prompts.find(p => p.id === promptId)
    if (prompt) {
      setSelectedPrompt(prompt)
      setIsEditing(false)
    } else {
      try {
        const loadedPrompt = await loadPrompt(promptId)
        setSelectedPrompt({ ...loadedPrompt, id: promptId })
      } catch {
        toast({
          title: "Error",
          description: "Failed to load the selected prompt.",
          variant: "destructive",
        })
      }
    }
    setIsLoading(false)
  }

  const handleCreateNewPrompt = () => {
    const newPrompt: Prompt = {
      id: Date.now().toString(),
      name: 'New Prompt',
      content: '',
    }
    setPrompts([...prompts, newPrompt])
    setSelectedPrompt(newPrompt)
    setIsEditing(true)
  }

  const handleSavePrompt = async () => {
    if (selectedPrompt) {
      setIsLoading(true)
      try {
        await savePrompt(selectedPrompt)
        setPrompts(prompts.map(p => (p.id === selectedPrompt.id ? selectedPrompt : p)))
        setIsEditing(false)
        toast({
          title: "Prompt saved",
          description: "Your prompt has been successfully saved.",
        })
      } catch {
        toast({
          title: "Error",
          description: "Failed to save the prompt.",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }
  }

  const handleDeletePrompt = async () => {
    if (selectedPrompt) {
      setIsLoading(true)
      try {
        await deletePrompt(selectedPrompt.name)
        setPrompts(prompts.filter(p => p.id !== selectedPrompt.id))
        setSelectedPrompt(null)
        setIsEditing(false)
        toast({
          title: "Prompt deleted",
          description: "The selected prompt has been deleted.",
          variant: "destructive",
        })
      } catch {
        toast({
          title: "Error",
          description: "Failed to delete the prompt.",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader className="bg-primary/10 rounded-t-lg">
          <CardTitle className="text-2xl font-bold flex items-center gap-2">
            <FileText className="h-6 w-6 text-primary" />
            Prompt Management
          </CardTitle>
          <CardDescription>View, edit, create, and delete prompts for your AI processing.</CardDescription>
        </CardHeader>
        <CardContent className="p-6 space-y-6">
          <div className="flex justify-between items-center">
            <Select onValueChange={handleSelectPrompt} value={selectedPrompt?.id || ""}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select a prompt" />
              </SelectTrigger>
              <SelectContent>
                {prompts.map(prompt => (
                  <SelectItem key={prompt.id} value={prompt.id}>
                    {prompt.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleCreateNewPrompt}>
              <Plus className="mr-2 h-4 w-4" /> New Prompt
            </Button>
          </div>
          <Card className="bg-secondary/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <List className="h-5 w-5 text-primary" />
                Prompt List
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px] w-full rounded-md border p-4">
                {prompts.map(prompt => (
                  <Button
                    key={prompt.id}
                    variant="ghost"
                    className="w-full justify-start mb-2"
                    onClick={() => handleSelectPrompt(prompt.id)}
                  >
                    <FileText className="mr-2 h-4 w-4" />
                    {prompt.name}
                  </Button>
                ))}
              </ScrollArea>
            </CardContent>
          </Card>
          {selectedPrompt && (
            <Card className="bg-muted/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg font-semibold flex items-center gap-2">
                  <FileText className="h-5 w-5 text-primary" />
                  {isEditing ? 'Edit Prompt' : 'Prompt Details'}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Prompt Name"
                  value={selectedPrompt.name}
                  onChange={(e) => setSelectedPrompt({ ...selectedPrompt, name: e.target.value })}
                  disabled={!isEditing || isLoading}
                />
                <Textarea
                  placeholder="Prompt Content"
                  value={selectedPrompt.content}
                  onChange={(e) => setSelectedPrompt({ ...selectedPrompt, content: e.target.value })}
                  disabled={!isEditing || isLoading}
                  className="min-h-[200px]"
                />
              </CardContent>
              <CardFooter className="flex justify-end space-x-2">
                {isEditing ? (
                  <Button onClick={handleSavePrompt} disabled={isLoading}>
                    <Save className="mr-2 h-4 w-4" /> Save
                  </Button>
                ) : (
                  <Button onClick={() => setIsEditing(true)} disabled={isLoading}>
                    <Edit2 className="mr-2 h-4 w-4" /> Edit
                  </Button>
                )}
                <Button variant="destructive" onClick={handleDeletePrompt} disabled={isLoading}>
                  <Trash2 className="mr-2 h-4 w-4" /> Delete
                </Button>
              </CardFooter>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  )
}