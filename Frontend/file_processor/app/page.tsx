import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Settings, MessageSquare, FolderOpen, Play, FileText } from 'lucide-react'

export default function Home() {
  const steps = [
    { name: "Configuration", href: "/config", icon: Settings, description: "Set up your processing parameters" },
    { name: "Prompt Management", href: "/prompt-management", icon: MessageSquare, description: "Manage and customize AI prompts" },
    { name: "File Management", href: "/file-management", icon: FolderOpen, description: "Upload and organize your files" },
    { name: "Processing", href: "/processing", icon: Play, description: "Run AI processing on your files" },
    { name: "Results", href: "/results", icon: FileText, description: "View and analyze processed results" },
  ]

  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-12 px-4 bg-background">
      <Card className="w-full max-w-3xl">
        <CardHeader className="text-center">
          <CardTitle className="text-4xl font-bold mb-2">File Processing App</CardTitle>
          <CardDescription className="text-xl">
            Process your files with AI in 5 simple steps
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {steps.map((step, index) => (
            <Link key={step.name} href={step.href} className="block">
              <Card className="transition-colors hover:bg-accent">
                <CardContent className="flex items-center p-4">
                  <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary text-primary-foreground font-bold mr-4">
                    {index + 1}
                  </div>
                  <div className="flex-grow">
                    <h3 className="text-lg font-semibold">{step.name}</h3>
                    <p className="text-sm text-muted-foreground">{step.description}</p>
                  </div>
                  <step.icon className="w-6 h-6 text-primary" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}