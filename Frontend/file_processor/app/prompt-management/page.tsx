'use client'

import { useEffect, useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/hooks/use-toast"
import { Trash2, Plus, Save } from 'lucide-react'
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
  
  const { toast } = useToast()

  useEffect(() => {
    const fetchPrompts = async () => {
      try {
        const promptNames = await listPrompts()
        const fetchedPrompts = await Promise.all(
          promptNames.map(async (name) => {
            const prompt = await loadPrompt(name)
            return { ...prompt, id: name }
          })
        )
        setPrompts(fetchedPrompts)
      } catch {
        toast({
          title: "Error",
          description: "Failed to fetch prompts.",
          variant: "destructive",
        })
      }
    }
    fetchPrompts()
  }, [])

  const handleSelectPrompt = async (promptId: string) => {
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
      }
    }
  }

  const handleDeletePrompt = async () => {
    if (selectedPrompt) {
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
      }
    }
  }

  return (
    <div className="container mx-auto py-10">
      <Card className="max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>Prompt Management</CardTitle>
          <CardDescription>View, edit, create, and delete prompts for your AI processing.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex justify-between items-center">
            <Select onValueChange={handleSelectPrompt} value={selectedPrompt?.id || ""}>
              <SelectTrigger className="w-[200px] bg-white border border-gray-300">
                <SelectValue placeholder="Select a prompt" />
              </SelectTrigger>
              <SelectContent className="bg-white border border-gray-300 rounded-md shadow-lg">
                {prompts.map(prompt => (
                  <SelectItem
                    key={prompt.id}
                    value={prompt.id}
                    className="px-4 py-2 hover:bg-gray-100 focus:bg-gray-100 text-black"
                  >
                    {prompt.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleCreateNewPrompt}>
              <Plus className="mr-2 h-4 w-4" /> New Prompt
            </Button>
          </div>
          {selectedPrompt && (
            <div className="space-y-4">
              <Input
                placeholder="Prompt Name"
                value={selectedPrompt.name}
                onChange={(e) => setSelectedPrompt({ ...selectedPrompt, name: e.target.value })}
                disabled={!isEditing}
                className="bg-white border border-gray-300"
              />
              <Textarea
                placeholder="Prompt Content"
                value={selectedPrompt.content}
                onChange={(e) => setSelectedPrompt({ ...selectedPrompt, content: e.target.value })}
                disabled={!isEditing}
                className="min-h-[200px] bg-white border border-gray-300"
              />
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="destructive" onClick={handleDeletePrompt} disabled={!selectedPrompt}>
            <Trash2 className="mr-2 h-4 w-4" /> Delete
          </Button>
          <div className="space-x-2">
            {isEditing ? (
              <Button onClick={handleSavePrompt}>
                <Save className="mr-2 h-4 w-4" /> Save
              </Button>
            ) : (
              <Button onClick={() => setIsEditing(true)} disabled={!selectedPrompt}>
                Edit
              </Button>
            )}
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
