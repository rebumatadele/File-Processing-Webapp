'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation'; // Use next/navigation for App Router
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import axiosInstance from '@/api/axiosInstance';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Loader state
  const { toast } = useToast();
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true); // Start loader

    try {
      const response = await axiosInstance.post('/auth/login', {
        email,
        password,
      });
      const { access_token } = response.data;

      // Store the token in localStorage
      localStorage.setItem('access_token', access_token);

      // Optionally set a cookie for middleware
      document.cookie = `access_token=${access_token}; path=/`;

      // Dispatch custom event to notify Navbar of auth change
      window.dispatchEvent(new Event('authChange'));

      toast({
        title: 'Success',
        description: 'Logged in successfully',
      });

      router.push('/');
    } catch (error: unknown) {
      const errorMessage =
        (error as { response?: { data?: { detail?: string } } })
          .response?.data?.detail || 'Login failed';
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false); // Stop loader
    }
  };

  return (
    <div className="container mx-auto p-4 max-w-md">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <form onSubmit={handleLogin} className="space-y-4">
        <div>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Logging in...' : 'Login'}
        </Button>
      </form>
      <p className="text-sm mt-2">
        Don&apos;t have an account?{' '}
        <Link href="/signup" className="text-primary underline">
          Sign Up
        </Link>
      </p>
    </div>
  );
}
