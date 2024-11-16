"use client"
import React, { useState } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { clearCache } from '@/api/cacheUtils';
import { clearFiles } from '@/api/fileUtils';

const UsagePage = () => {
    const [cacheMessage, setCacheMessage] = useState('');
    const [fileMessage, setFileMessage] = useState('');

    const handleClearCache = async () => {
        try {
            setCacheMessage('Clearing cache...');
            const response = await clearCache();
            setCacheMessage(response.message || 'Cache cleared successfully.');
        } catch{
            setCacheMessage('Failed to clear cache.');
        }
    };

    const handleClearFiles = async () => {
        try {
            setFileMessage('Clearing files...');
            const response = await clearFiles();
            setFileMessage(response.message || 'All files cleared successfully.');
        } catch {
            setFileMessage('Failed to clear files.');
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Usage Information</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Card>
                    <CardHeader>
                        <h2 className="text-xl font-semibold">File Storage Usage</h2>
                    </CardHeader>
                    <CardContent>
                        <p>Current CPU usage is at 45%.</p>
                    </CardContent>
                    <CardFooter>
                        <div className="flex flex-col">
                            <Button onClick={handleClearFiles}>Clear All Files</Button>
                            {fileMessage && <p className="text-sm mt-2">{fileMessage}</p>}
                        </div>
                    </CardFooter>
                </Card>
                <Card>
                    <CardHeader>
                        <h2 className="text-xl font-semibold">Cache Usage</h2>
                    </CardHeader>
                    <CardContent>
                        <p>Current Memory usage is at 65%.</p>
                    </CardContent>
                    <CardFooter>
                        <div className="flex flex-col">
                            <Button onClick={handleClearCache}>Clear Cache</Button>
                            {cacheMessage && <p className="text-sm mt-2">{cacheMessage}</p>}
                        </div>
                    </CardFooter>
                </Card>
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