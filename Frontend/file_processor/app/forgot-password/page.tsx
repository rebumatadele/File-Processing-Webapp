// pages/forgot-password.tsx

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import axiosInstance from '@/api/axiosInstance';
import {
  ForgotPasswordResponse,
  ErrorResponse,
} from '@/types/apiTypes';
import axios from 'axios';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleForgotPassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Encode the email to safely include it in the URL
      const encodedEmail = encodeURIComponent(email.trim());

      // Make a POST request with email as a query parameter
      const response = await axiosInstance.post<ForgotPasswordResponse>(
        `/auth/forgot-password?email=${encodedEmail}`,
        {} // Empty body
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
      <h1 className="text-2xl font-bold mb-4">Forgot Password</h1>
      <form onSubmit={handleForgotPassword} className="space-y-4">
        <div>
          <Label htmlFor="email">Enter your email address</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send Reset Link'}
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
