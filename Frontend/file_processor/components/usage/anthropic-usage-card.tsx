// src/components/usage/anthropic-usage-card.tsx

"use client"

import React from "react"
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Progress } from "@/components/ui/progress"
import { CpuIcon, RefreshCw, AlertCircle } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface AnthropicUsageCardProps {
  data: {
    anthropic_usage: {
      requests_limit: number
      requests_remaining: number
      requests_reset_time: string | null
      tokens_limit: number
      tokens_remaining: number
      tokens_reset_time: string | null
      input_tokens_limit: number
      input_tokens_remaining: number
      input_tokens_reset_time: string | null
      output_tokens_limit: number
      output_tokens_remaining: number
      output_tokens_reset_time: string | null
    }
    last_updated: string
  } | null
  loading: boolean
  onRefresh: () => void
}

export function AnthropicUsageCard({ data, loading, onRefresh }: AnthropicUsageCardProps) {
  const metrics = [
    { name: "Requests", key: "requests" },
    { name: "Total Tokens", key: "tokens" },
    { name: "Input Tokens", key: "input_tokens" },
    { name: "Output Tokens", key: "output_tokens" },
  ] as const

  const formatNumber = (num: number) => new Intl.NumberFormat().format(num)

  const getProgressColor = (remaining: number, limit: number) => {
    const percentage = (remaining / limit) * 100
    if (percentage > 66) return "bg-green-500"
    if (percentage > 33) return "bg-yellow-500"
    return "bg-red-500"
  }

  /**
   * Safely calculates the hours until reset.
   * Returns "N/A" if resetTime is invalid or in the past.
   */
  const calculateHoursUntilReset = (resetTimeStr: string | null): string | number => {
    if (!resetTimeStr) return "N/A"

    const resetTime = new Date(resetTimeStr)
    if (isNaN(resetTime.getTime())) return "N/A"

    const diffInMs = resetTime.getTime() - Date.now()
    if (diffInMs <= 0) return "N/A"

    const diffInHours = Math.ceil(diffInMs / (1000 * 60 * 60))
    return diffInHours
  }

  return (
    <Card className="shadow-lg overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CpuIcon className="h-6 w-6" />
            <h2 className="text-xl font-bold">Anthropic Usage</h2>
          </div>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={onRefresh} disabled={loading}>
                  <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>{loading ? "Refreshing..." : "Refresh data"}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        {loading ? (
          <div className="space-y-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-1/4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-2 w-full" />
              </div>
            ))}
          </div>
        ) : data ? (
          <div className="space-y-6">
            {metrics.map((metric) => {
              const limit = data.anthropic_usage[`${metric.key}_limit` as keyof typeof data.anthropic_usage]
              const remaining = data.anthropic_usage[`${metric.key}_remaining` as keyof typeof data.anthropic_usage]
              const resetTimeStr = data.anthropic_usage[`${metric.key}_reset_time` as keyof typeof data.anthropic_usage] as string | null
              const hoursUntilReset = calculateHoursUntilReset(resetTimeStr)
              const used = Number(limit) - Number(remaining)
              const progressColor = getProgressColor(Number(remaining), Number(limit))

              return (
                <div key={metric.key} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <h3 className="font-medium text-sm text-gray-600">{metric.name}</h3>
                    <span className="text-xs text-gray-500">
                      {formatNumber(used)} / {formatNumber(Number(limit))}
                    </span>
                  </div>
                  <Progress value={(used / Number(limit)) * 100} className={`h-2 ${progressColor}`} />
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>{formatNumber(Number(remaining))} remaining</span>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <div className="flex items-center cursor-help">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            {typeof hoursUntilReset === "number" ? `Resets in ${hoursUntilReset}h` : "N/A"}
                          </div>
                        </TooltipTrigger>
                        {typeof resetTimeStr === "string" && resetTimeStr ? (
                          <TooltipContent>
                            <p>Resets on: {new Date(resetTimeStr).toLocaleString()}</p>
                          </TooltipContent>
                        ) : (
                          <TooltipContent>
                            <p>Reset time unavailable.</p>
                          </TooltipContent>
                        )}
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="flex items-center justify-center h-40 text-gray-500">
            <p className="text-sm">No Anthropic usage data available.</p>
          </div>
        )}
      </CardContent>
      <CardFooter className="bg-gray-50 text-xs text-gray-500 flex justify-end items-center py-2 px-4">
        Last updated: {data ? new Date(data.last_updated).toLocaleString() : "N/A"}
      </CardFooter>
    </Card>
  )
}
