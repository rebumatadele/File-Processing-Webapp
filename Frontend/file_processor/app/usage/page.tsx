// src/pages/UsagePage.tsx

"use client"

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { clearCache, getCacheSize, listCacheContents } from '@/api/cacheUtils';
import { clearFiles, listFiles, getFileContent } from '@/api/fileUtils';
import { getAllResults } from '@/api/resultsUtils';
import { ProcessingResult } from '@/types/apiTypes';

const UsagePage = () => {
    const [cacheMessage, setCacheMessage] = useState<string>('');
    const [fileMessage, setFileMessage] = useState<string>('');
    const [cacheSize, setCacheSize] = useState<number | null>(null);
    const [cacheContents, setCacheContents] = useState<string[]>([]);
    const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
    const [uploadedFilesSize, setUploadedFilesSize] = useState<number | null>(null);
    const [processedFiles, setProcessedFiles] = useState<ProcessingResult[]>([]);
    const [processedFilesSize, setProcessedFilesSize] = useState<number | null>(null);
    const [loadingCache, setLoadingCache] = useState<boolean>(false);
    const [loadingFiles, setLoadingFiles] = useState<boolean>(false);
    const [loadingProcessed, setLoadingProcessed] = useState<boolean>(false);

    // Fetch Cache Information
    const fetchCacheInfo = async () => {
        setLoadingCache(true);
        try {
            const sizeResponse = await getCacheSize();
            setCacheSize(sizeResponse.cache_size_bytes);
            const contentsResponse = await listCacheContents();
            setCacheContents(contentsResponse.cache_contents);
        } catch (error) {
            console.error("Failed to fetch cache info:", error);
        } finally {
            setLoadingCache(false);
        }
    };

    // Fetch Uploaded Files and Their Sizes
    const fetchUploadedFiles = async () => {
        setLoadingFiles(true);
        try {
            const files = await listFiles();
            setUploadedFiles(files);
            // Calculate total uploaded files size
            let totalSize = 0;
            for (const filename of files) {
                const fileInfo = await getFileContent(filename);
                const size = new Blob([fileInfo.content]).size;
                totalSize += size;
            }
            setUploadedFilesSize(totalSize);
        } catch (error) {
            console.error("Failed to fetch uploaded files:", error);
        } finally {
            setLoadingFiles(false);
        }
    };

    // Fetch Processed Files and Their Sizes
    const fetchProcessedFiles = async () => {
        setLoadingProcessed(true);
        try {
            const resultsResponse = await getAllResults();
            const results: ProcessingResult[] = Object.entries(resultsResponse).map(([filename, content]) => ({
                filename,
                content,
            }));
            setProcessedFiles(results);
            // Calculate total processed files size
            let totalSize = 0;
            results.forEach(result => {
                totalSize += new Blob([result.content]).size;
            });
            setProcessedFilesSize(totalSize);
        } catch (error) {
            console.error("Failed to fetch processed files:", error);
        } finally {
            setLoadingProcessed(false);
        }
    };

    useEffect(() => {
        fetchCacheInfo();
        fetchUploadedFiles();
        fetchProcessedFiles();
    }, []);

    const handleClearCache = async () => {
        try {
            setCacheMessage('Clearing cache...');
            const response = await clearCache();
            setCacheMessage(response.message || 'Cache cleared successfully.');
            fetchCacheInfo(); // Refresh cache info
        } catch {
            setCacheMessage('Failed to clear cache.');
        }
    };

    const handleClearFiles = async () => {
        try {
            setFileMessage('Clearing files...');
            const response = await clearFiles();
            setFileMessage(response.message || 'All files cleared successfully.');
            fetchUploadedFiles(); // Refresh uploaded files
            fetchProcessedFiles(); // Refresh processed files
        } catch {
            setFileMessage('Failed to clear files.');
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Usage Information</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* File Storage Usage Card */}
                <Card>
                    <CardHeader>
                        <h2 className="text-xl font-semibold">File Storage Usage</h2>
                    </CardHeader>
                    <CardContent>
                        <p>Uploaded Files Size: {loadingFiles ? 'Loading...' : `${uploadedFilesSize !== null ? (uploadedFilesSize / (1024)).toFixed(2) : 'N/A'} KB`}</p>
                        <p>Uploaded Files:</p>
                        <ul className="list-disc list-inside">
                            {uploadedFiles.length > 0 ? (
                                uploadedFiles.map((file, index) => <li key={index}>{file}</li>)
                            ) : (
                                <li>No uploaded files.</li>
                            )}
                        </ul>
                    </CardContent>
                    <CardFooter>
                        <div className="flex flex-col">
                            <Button onClick={handleClearFiles}>Clear All Files</Button>
                            {fileMessage && <p className="text-sm mt-2">{fileMessage}</p>}
                        </div>
                    </CardFooter>
                </Card>

                {/* Cache Usage Card */}
                <Card>
                    <CardHeader>
                        <h2 className="text-xl font-semibold">Cache Usage</h2>
                    </CardHeader>
                    <CardContent>
                        <p>Cache Size: {loadingCache ? 'Loading...' : `${cacheSize !== null ? (cacheSize / (1024)).toFixed(2) : 'N/A'} KB`}</p>
                        <div className="mt-2">
                            <h3 className="text-md font-medium">Cache Contents:</h3>
                            {loadingCache ? (
                                <p>Loading...</p>
                            ) : (
                                <ul className="list-disc list-inside">
                                    {cacheContents.length > 0 ? (
                                        cacheContents.map((item, index) => <li key={index}>{item}</li>)
                                    ) : (
                                        <li>No cache entries.</li>
                                    )}
                                </ul>
                            )}
                        </div>
                    </CardContent>
                    <CardFooter>
                        <div className="flex flex-col">
                            <Button onClick={handleClearCache}>Clear Cache</Button>
                            {cacheMessage && <p className="text-sm mt-2">{cacheMessage}</p>}
                        </div>
                    </CardFooter>
                </Card>

                {/* Processed Files Usage Card */}
                <Card>
                    <CardHeader>
                        <h2 className="text-xl font-semibold">Processed Files</h2>
                    </CardHeader>
                    <CardContent>
                        <p>Processed Files Size: {loadingProcessed ? 'Loading...' : `${processedFilesSize !== null ? (processedFilesSize / (1024)).toFixed(2) : 'N/A'} KB`}</p>
                        <p>Processed Files:</p>
                        <ul className="list-disc list-inside">
                            {processedFiles.length > 0 ? (
                                processedFiles.map((file, index) => <li key={index}>{file.filename}</li>)
                            ) : (
                                <li>No processed files.</li>
                            )}
                        </ul>
                    </CardContent>
                    <CardFooter>
                        <p>Updated {new Date().toLocaleTimeString()}</p>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
};

export default UsagePage;
