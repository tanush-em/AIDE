'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Menu, 
  X, 
  Home, 
  Calendar, 
  BookOpen, 
  Users, 
  Bell, 
  Settings, 
  LogOut,
  GraduationCap,
  FileText,
  BarChart3,
  MessageSquare,
  Sparkles
} from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      router.push('/login');
    }
  }, [router]);

  useEffect(() => {
    // Mock notifications - in real app, these would come from API
    setNotifications([
      { id: 1, message: 'New assignment uploaded', time: '2 hours ago', type: 'info' },
      { id: 2, message: 'Low attendance warning', time: '1 day ago', type: 'warning' },
    ]);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    router.push('/login');
  };

  const getMenuItems = (role) => {
    const baseItems = [
      { name: 'Dashboard', href: `/dashboard/${role}`, icon: Home },
      { name: 'Notifications', href: `/dashboard/${role}/notifications`, icon: Bell },
      { name: 'Settings', href: `/dashboard/${role}/settings`, icon: Settings },
    ];

    if (role === 'student') {
      return [
        ...baseItems,
        { name: 'Timetable', href: `/dashboard/${role}/timetable`, icon: Calendar },
        { name: 'Attendance', href: `/dashboard/${role}/attendance`, icon: BarChart3 },
        { name: 'Resources', href: `/dashboard/${role}/resources`, icon: BookOpen },
        { name: 'Leave Applications', href: `/dashboard/${role}/leave`, icon: FileText },
        { name: 'AI Assistant', href: `/dashboard/${role}/assistant`, icon: MessageSquare },
      ];
    } else if (role === 'faculty') {
      return [
        ...baseItems,
        { name: 'Classes', href: `/dashboard/${role}/classes`, icon: Users },
        { name: 'Resources', href: `/dashboard/${role}/resources`, icon: BookOpen },
        { name: 'Question Papers', href: `/dashboard/${role}/questions`, icon: FileText },
        { name: 'Attendance', href: `/dashboard/${role}/attendance`, icon: BarChart3 },
        { name: 'Leave Requests', href: `/dashboard/${role}/leave-requests`, icon: Calendar },
        { name: 'AI Assistant', href: `/dashboard/${role}/assistant`, icon: MessageSquare },
      ];
    } else if (role === 'coordinator') {
      return [
        ...baseItems,
        { name: 'Events', href: `/dashboard/${role}/events`, icon: Calendar },
        { name: 'Registrations', href: `/dashboard/${role}/registrations`, icon: Users },
        { name: 'Notifications', href: `/dashboard/${role}/notifications`, icon: Bell },
        { name: 'Reports', href: `/dashboard/${role}/reports`, icon: BarChart3 },
        { name: 'AI Assistant', href: `/dashboard/${role}/assistant`, icon: MessageSquare },
      ];
    }

    return baseItems;
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const menuItems = getMenuItems(user.role);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200 dark:border-slate-700">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                AIDE
              </span>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* User Info */}
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-medium text-slate-900 dark:text-slate-100">{user.name}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400 capitalize">{user.role}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {menuItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                  }`}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-700">
            <button
              onClick={handleLogout}
              className="flex items-center space-x-3 w-full px-3 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all duration-200"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-4">
              {/* Notifications */}
              <div className="relative">
                <button className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 relative">
                  <Bell className="w-5 h-5" />
                  {notifications.length > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                      {notifications.length}
                    </span>
                  )}
                </button>
              </div>

              {/* User menu */}
              <div className="flex items-center space-x-3">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{user.name}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 capitalize">{user.role}</p>
                </div>
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <GraduationCap className="w-4 h-4 text-white" />
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
} 