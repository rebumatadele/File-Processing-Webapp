// src/app/reset-password/page.tsx

'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import axiosInstance from '@/api/axiosInstance';
import {
  ResetPasswordRequest,
  ResetPasswordResponse,
  ErrorResponse,
} from '@/types/apiTypes';
import axios from 'axios';

export default function ResetPasswordPage() {
  const [newPassword, setNewPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { toast } = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();

  const token = searchParams.get('token');

  useEffect(() => {
    if (!token) {
      toast({
        title: 'Error',
        description: 'Invalid or missing token.',
        variant: 'destructive',
      });
      router.push('/forgot-password');
    }
  }, [token, toast, router]);

  const handleResetPassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (newPassword !== confirmPassword) {
      toast({
        title: 'Error',
        description: 'Passwords do not match.',
        variant: 'destructive',
      });
      return;
    }

    if (!token) {
      toast({
        title: 'Error',
        description: 'Invalid or missing token.',
        variant: 'destructive',
      });
      router.push('/forgot-password');
      return;
    }

    setIsLoading(true);

    const requestData: ResetPasswordRequest = { new_password: newPassword };

    // Debugging: Log the token and requestData
    console.log('Reset Password Request Data:', requestData);
    console.log('Authorization Token:', token);

    try {
      const response = await axiosInstance.post<ResetPasswordResponse>(
        '/auth/reset-password',
        requestData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            // 'Content-Type': 'application/json', // Axios sets this automatically
          },
        }
      );

      toast({
        title: 'Success',
        description: response.data.message,
      });
      router.push('/login');
    } catch (error: unknown) {
      let errorMessage: string = 'Something went wrong';

      if (axios.isAxiosError<ErrorResponse>(error)) {
        if (error.response?.data?.detail) {
          if (Array.isArray(error.response.data.detail)) {
            // Concatenate all error messages
            errorMessage = error.response.data.detail
              .map((err) => err.msg)
              .join(', ');
          } else if (typeof error.response.data.detail === 'string') {
            errorMessage = error.response.data.detail;
          }
        }
      }

      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-md">
      <h1 className="text-2xl font-bold mb-4">Reset Password</h1>
      <form onSubmit={handleResetPassword} className="space-y-4">
        <div>
          <Label htmlFor="newPassword">New Password</Label>
          <Input
            id="newPassword"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
            minLength={6} // Enforce minimum password length
          />
        </div>
        <div>
          <Label htmlFor="confirmPassword">Confirm New Password</Label>
          <Input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            minLength={6} // Enforce minimum password length
          />
        </div>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Resetting...' : 'Reset Password'}
        </Button>
      </form>
      <p className="text-sm mt-2">
        Remembered your password?{' '}
        <Link href="/login" className="text-primary underline">
          Login
        </Link>
      </p>
    </div>
  );
}
