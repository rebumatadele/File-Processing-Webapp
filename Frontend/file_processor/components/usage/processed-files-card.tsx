// src/components/usage/processed-files-card.tsx

import React from "react"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import { CpuIcon } from "lucide-react"

interface ProcessedFilesCardProps {
  data: { files: { filename: string; content: string }[]; size: number | null }
  loading: boolean
  lastUpdated: string
}

export function ProcessedFilesCard({ data, loading, lastUpdated }: ProcessedFilesCardProps) {
  return (
    <Card className="shadow-lg">
      <CardHeader className="bg-accent/10 rounded-t-lg">
        <div className="flex items-center space-x-2">
          <CpuIcon className="text-accent" />
          <h2 className="text-xl font-semibold">Processed Files</h2>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Changed <p> to <div> to avoid invalid nesting */}
          <div className="text-lg font-medium">
            Processed Files Size:{" "}
            {loading ? (
              <Skeleton className="h-4 w-24 inline-block" />
            ) : (
              <span className="text-accent">
                {data.size !== null ? `${(data.size / 1024).toFixed(2)} KB` : "N/A"}
              </span>
            )}
          </div>
          <div>
            <h3 className="text-md font-medium mb-2">Processed Files:</h3>
            <ScrollArea className="h-40 rounded-md border p-2">
              {loading ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                </div>
              ) : data.files.length > 0 ? (
                data.files.map((file, index) => (
                  <p key={index} className="text-sm py-1">
                    {file.filename}
                  </p>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No processed files.</p>
              )}
            </ScrollArea>
          </div>
        </div>
      </CardContent>
      <CardFooter className="bg-accent/5 rounded-b-lg flex justify-between items-center text-sm text-muted-foreground">
        <span>Last updated: {lastUpdated || "Fetching..."}</span>
      </CardFooter>
    </Card>
  )
}