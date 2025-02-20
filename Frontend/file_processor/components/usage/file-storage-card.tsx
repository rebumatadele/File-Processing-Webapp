// src/components/usage/file-storage-card.tsx

import React from "react"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import { FileIcon } from "lucide-react"

interface FileStorageCardProps {
  data: { files: string[]; size: number | null }
  loading: boolean
  onClearFiles: () => void
}

export function FileStorageCard({ data, loading, onClearFiles }: FileStorageCardProps) {
  return (
    <Card className="shadow-lg">
      <CardHeader className="bg-secondary/10 rounded-t-lg">
        <div className="flex items-center space-x-2">
          <FileIcon className="text-secondary" />
          <h2 className="text-xl font-semibold">File Storage Usage</h2>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Changed <p> to <div> to avoid invalid nesting */}
          <div className="text-lg font-medium">
            Uploaded Files Size:{" "}
            {loading ? (
              <Skeleton className="h-4 w-24 inline-block" />
            ) : (
              <span className="text-primary">
                {data.size !== null ? `${(data.size / 1024).toFixed(2)} KB` : "N/A"}
              </span>
            )}
          </div>
          <div>
            <h3 className="text-md font-medium mb-2">Uploaded Files:</h3>
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
                    {file}
                  </p>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No uploaded files.</p>
              )}
            </ScrollArea>
          </div>
        </div>
      </CardContent>
      <CardFooter className="bg-secondary/5 rounded-b-lg">
        <Button onClick={onClearFiles} variant="outline" className="w-full" disabled={loading}>
          {loading ? "Clearing..." : "Clear All Files"}
        </Button>
      </CardFooter>
    </Card>
  )
}
