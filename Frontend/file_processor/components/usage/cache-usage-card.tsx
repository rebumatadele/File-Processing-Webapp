// src/components/usage/cache-usage-card.tsx

import React from "react"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { ScrollArea } from "@/components/ui/scroll-area"
import { DatabaseIcon } from "lucide-react"

interface CacheUsageCardProps {
  data: { size: number | null; contents: string[] }
  loading: boolean
  onClearCache: () => void
}

export function CacheUsageCard({
  data,
  loading,
  onClearCache
}: CacheUsageCardProps) {
  // Convert bytes -> kilobytes
  const sizeInKB = data.size !== null ? (data.size / 1024).toFixed(2) : "N/A"

  return (
    <Card className="shadow-lg">
      <CardHeader className="bg-primary/10 rounded-t-lg">
        <div className="flex items-center space-x-2">
          <DatabaseIcon className="text-primary" />
          <h2 className="text-xl font-semibold">Cache Usage</h2>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="text-lg font-medium">
            Cache Size:{" "}
            {loading ? (
              <Skeleton className="h-4 w-24 inline-block" />
            ) : (
              <span className="text-primary">
                {sizeInKB !== "N/A" ? `${sizeInKB} KB` : "N/A"}
              </span>
            )}
          </div>
          <div>
            <h3 className="text-md font-medium mb-2">Cache Contents:</h3>
            <ScrollArea className="h-40 rounded-md border p-2">
              {loading ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                </div>
              ) : data.contents.length > 0 ? (
                data.contents.map((item, index) => (
                  <p key={index} className="text-sm py-1">
                    {item}
                  </p>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No cache entries.</p>
              )}
            </ScrollArea>
          </div>
        </div>
      </CardContent>
      <CardFooter className="bg-primary/5 rounded-b-lg">
        <Button
          onClick={onClearCache}
          variant="outline"
          className="w-full"
          disabled={loading}
        >
          {loading ? "Clearing..." : "Clear Cache"}
        </Button>
      </CardFooter>
    </Card>
  )
}
