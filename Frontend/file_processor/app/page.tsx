'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Settings, MessageSquare, FolderOpen, Play, FileText, ChevronRight } from 'lucide-react'

const steps = [
  { name: "Configuration", href: "/config", icon: Settings, description: "Set up your processing parameters" },
  { name: "Prompt Management", href: "/prompt-management", icon: MessageSquare, description: "Manage and customize AI prompts" },
  { name: "File Management", href: "/file-management", icon: FolderOpen, description: "Upload and organize your files" },
  { name: "Processing", href: "/processing", icon: Play, description: "Run AI processing on your files" },
  { name: "Batch Processing", href: "/claude_batch_processing", icon: Play, description: "Run Batch Claude AI processing on your files" },
  { name: "Results", href: "/results", icon: FileText, description: "View and analyze processed results" },
]

const testimonials = [
  { name: "Rebuma Tadele", role: "Developer", quote: "This app has revolutionized our document processing workflow!" },
  { name: "Rebuma Tadele", role: "Developer", quote: "This app has revolutionized our document processing workflow!" },
  { name: "Rebuma Tadele", role: "Developer", quote: "This app has revolutionized our document processing workflow!" }
]

export default function Home() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-background to-primary/10">
      <main className="w-full max-w-6xl mx-auto px-4 py-12 space-y-16">
        {/* Hero Section */}
        <section className="text-center space-y-6">
          <motion.h1 
            className="text-5xl font-bold text-primary"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            AI-Powered File Processing
          </motion.h1>
          <motion.p 
            className="text-xl text-muted-foreground max-w-2xl mx-auto"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            Transform your documents with cutting-edge AI technology. Streamline your workflow and unlock valuable insights in minutes.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Button size="lg" asChild>
              <Link href="/config">Get Started <ChevronRight className="ml-2 h-4 w-4" /></Link>
            </Button>
          </motion.div>
        </section>

        {/* Steps Section */}
        <section>
          <h2 className="text-3xl font-bold text-center mb-8">Process Your Files in 5 Simple Steps</h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {steps.map((step, index) => (
              <motion.div
                key={step.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Link href={step.href}>
                  <Card className="h-full transition-all hover:shadow-lg hover:scale-105">
                    <CardContent className="flex flex-col items-center p-6 text-center">
                      <div className="rounded-full bg-primary/10 p-3 mb-4">
                        <step.icon className="w-6 h-6 text-primary" />
                      </div>
                      <h3 className="text-lg font-semibold mb-2">{step.name}</h3>
                      <p className="text-sm text-muted-foreground">{step.description}</p>
                    </CardContent>
                  </Card>
                </Link>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Features Section */}
        <section className="bg-primary/5 rounded-lg p-8">
          <h2 className="text-3xl font-bold text-center mb-8">Powerful Features</h2>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard title="AI-Powered Analysis" description="Leverage cutting-edge AI models to extract insights from your documents." />
            <FeatureCard title="Customizable Prompts" description="Tailor the AI's focus with our flexible prompt management system." />
            <FeatureCard title="Batch Processing" description="Handle large volumes of files efficiently with our robust processing engine." />
            <FeatureCard title="Secure File Handling" description="Your data's security is our priority. All files are processed with utmost care." />
            <FeatureCard title="Detailed Results" description="Get comprehensive analysis results with easy-to-understand visualizations." />
            <FeatureCard title="Integration Ready" description="Seamlessly integrate our processing capabilities into your existing workflow." />
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="text-center">
          <h2 className="text-3xl font-bold mb-8">What Our Users Say</h2>
          <Card className="max-w-2xl mx-auto">
            <CardContent className="p-6">
              <motion.div
                key={currentTestimonial}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                <p className="text-lg italic mb-4">&quot;{testimonials[currentTestimonial].quote}&quot;</p>
                <p className="font-semibold">{testimonials[currentTestimonial].name}</p>
                <p className="text-sm text-muted-foreground">{testimonials[currentTestimonial].role}</p>
              </motion.div>
            </CardContent>
          </Card>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-primary text-primary-foreground rounded-lg p-8">
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Document Processing?</h2>
          <p className="text-xl mb-6">Join and experience the power of AI-driven analysis.</p>
          <Button size="lg" variant="secondary" asChild>
            <Link href="/config">Start <ChevronRight className="ml-2 h-4 w-4" /></Link>
          </Button>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full bg-background py-6 mt-16">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-muted-foreground">&copy; 2024 AI File Processor. All rights reserved.</p>
          <nav className="flex gap-4 mt-4 md:mt-0">
            <Link href="#" className="text-sm text-muted-foreground hover:text-primary">Privacy Policy</Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-primary">Terms of Service</Link>
            <Link href="#" className="text-sm text-muted-foreground hover:text-primary">Contact Us</Link>
          </nav>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <Card>
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}