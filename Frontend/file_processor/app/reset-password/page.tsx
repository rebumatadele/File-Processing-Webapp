// src/app/reset-password/page.tsx

'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import resetPasswordInstance from '@/api/resetPasswordInstance'; // Import the new Axios instance
import {
  ResetPasswordResponse,
  ErrorResponse,
} from '@/types/apiTypes';
import axios from 'axios';

// **Component that contains the Reset Password Form**
function ResetPasswordForm({ token }: { token: string }) {
  const [newPassword, setNewPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleResetPassword = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // **Password Match Validation**
    if (newPassword !== confirmPassword) {
      toast({
        title: 'Error',
        description: 'Passwords do not match.',
        variant: 'destructive',
      });
      return;
    }

    // **Ensure Password is Not Empty or Whitespace**
    if (newPassword.trim() === '') {
      toast({
        title: 'Error',
        description: 'Password cannot be empty.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);

    // **Prepare Request Data as an Object**
    const requestData = { new_password: newPassword };

    // **Debugging Logs**
    console.log('Reset Password Request Data:', requestData);
    console.log('Authorization Token:', token);

    try {
      // **API Call to Reset Password**
      const response = await resetPasswordInstance.post<ResetPasswordResponse>(
        '/auth/reset-password',
        requestData, // Send as JSON object
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      // **Success Toast and Redirection**
      toast({
        title: 'Success',
        description: response.data.message,
      });
      router.push('/login');
    } catch (error: unknown) {
      let errorMessage: string = 'Something went wrong';

      // **Error Handling**
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

      // **Error Toast**
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
            // Removed minLength
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
            // Removed minLength
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

// **Main Page Component with Suspense Boundary**
export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  return (
    <Suspense fallback={<div>Loading...</div>}>
      {token ? (
        <ResetPasswordForm token={token} />
      ) : (
        <div className="container mx-auto p-4 max-w-md">
          <h1 className="text-2xl font-bold mb-4">Reset Password</h1>
          <p className="text-sm mt-2">
            Invalid or missing token. Please{' '}
            <Link href="/forgot-password" className="text-primary underline">
              request a new password reset
            </Link>
            .
          </p>
        </div>
      )}
    </Suspense>
  );
}
