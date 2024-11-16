// src/pages/UsagePage.tsx

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { clearCache, getCacheSize, listCacheContents } from '@/api/cacheUtils';
import { clearFiles as clearAllFiles } from '@/api/fileUtils';

const UsagePage = () => {
    const [cacheMessage, setCacheMessage] = useState('');
    const [fileMessage, setFileMessage] = useState('');
    const [cacheSize, setCacheSize] = useState<number | null>(null);
    const [cacheContents, setCacheContents] = useState<string[]>([]);
    const [loadingCache, setLoadingCache] = useState<boolean>(false);

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

    useEffect(() => {
        fetchCacheInfo();
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
            const response = await clearAllFiles();
            setFileMessage(response.message || 'All files cleared successfully.');
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
                        <p>Current CPU usage is at 45%.</p>
                        <p>Uploaded Files Size: {fileMessage ? fileMessage : 'Loading...'}</p>
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
                        <p>Current Memory usage is at 65%.</p>
                        <p>Cache Size: {loadingCache ? 'Loading...' : `${cacheSize !== null ? cacheSize : 'N/A'} bytes`}</p>
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

                {/* Token Usage Card */}
                <Card>
                    <CardHeader>
                        <h2 className="text-xl font-semibold">Token Usage</h2>
                    </CardHeader>
                    <CardContent>
                        <p>Current Disk usage is at 70%.</p>
                    </CardContent>
                    <CardFooter>
                        <p>Updated 2 minutes ago</p>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
};

export default UsagePage;