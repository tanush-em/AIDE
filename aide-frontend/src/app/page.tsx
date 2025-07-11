"use client";
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';

export default function Home() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.replace('/login');
    } else if (user.role === 'student') {
      router.replace('/student/dashboard');
    } else if (user.role === 'teacher') {
      router.replace('/teacher/dashboard');
    }
  }, [user, router]);

  return null;
}
