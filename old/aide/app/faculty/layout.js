'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Menu, 
  X, 
  Home, 
  Calendar, 
  BookOpen, 
  Bell, 
  Settings, 
  LogOut,
  Users,
  FileText,
  BarChart3,
  MessageSquare,
  Sparkles,
  ClipboardList,
  Plus,
  Edit,
  Upload,
  Award,
  Shield
} from 'lucide-react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';

export default function FacultyLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const userObj = JSON.parse(userData);
      if (userObj.role !== 'faculty') {
        router.push('/login');
        return;
      }
      setUser(userObj);
    } else {
      router.push('/login');
    }
  }, [router]);

  useEffect(() => {
    // Mock notifications - in real app, these would come from API
    setNotifications([
      { id: 1, message: 'New leave request from John Doe', time: '1 hour ago', type: 'info' },
      { id: 2, message: 'Assignment submission deadline approaching', time: '3 hours ago', type: 'warning' },
      { id: 3, message: 'Staff meeting scheduled for tomorrow', time: '5 hours ago', type: 'info' },
    ]);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    router.push('/login');
  };

  const menuItems = [
    {
      section: 'Overview',
      items: [
        { name: 'Dashboard', href: '/faculty', icon: Home },
        { name: 'AI Assistant', href: '/faculty/assistant', icon: MessageSquare },
      ]
    },
    {
      section: 'Teaching',
      items: [
        { name: 'My Classes', href: '/faculty/classes', icon: Users },
        { name: 'Attendance', href: '/faculty/attendance', icon: BarChart3 },
        { name: 'Assignments', href: '/faculty/assignments', icon: FileText },
        { name: 'Question Papers', href: '/faculty/questions', icon: ClipboardList },
        { name: 'Study Materials', href: '/faculty/materials', icon: BookOpen },
      ]
    },
    {
      section: 'Administration',
      items: [
        { name: 'Leave Requests', href: '/faculty/leave-requests', icon: Calendar },
        { name: 'Notice Board', href: '/faculty/notices', icon: Bell },
        { name: 'Student Management', href: '/faculty/students', icon: Users },
        { name: 'Results', href: '/faculty/results', icon: Award },
        { name: 'Reports', href: '/faculty/reports', icon: BarChart3 },
      ]
    }
  ];

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex">
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
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 lg:block`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-slate-200 dark:border-slate-700">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-pink-500 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent">
                AIDE Faculty
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
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-medium text-slate-900 dark:text-slate-100">{user.name}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">Faculty</p>
                <p className="text-xs text-slate-400 dark:text-slate-500">ID: {user.id}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-6 overflow-y-auto">
            {menuItems.map((section) => (
              <div key={section.section}>
                <h3 className="px-3 mb-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  {section.section}
                </h3>
                <div className="space-y-1">
                  {section.items.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                          isActive
                            ? 'bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800'
                            : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                        }`}
                        onClick={() => setSidebarOpen(false)}
                      >
                        <item.icon className="w-5 h-5" />
                        <span className="font-medium">{item.name}</span>
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>

          {/* Quick Actions */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-700">
            <h3 className="px-3 mb-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Quick Actions
            </h3>
            <div className="space-y-2">
              <button className="flex items-center space-x-3 w-full px-3 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all duration-200">
                <Plus className="w-5 h-5" />
                <span className="font-medium">Add Notice</span>
              </button>
              <button className="flex items-center space-x-3 w-full px-3 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all duration-200">
                <Upload className="w-5 h-5" />
                <span className="font-medium">Upload Material</span>
              </button>
            </div>
          </div>

          {/* Settings & Logout */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-700 space-y-2">
            <Link
              href="/faculty/settings"
              className="flex items-center space-x-3 w-full px-3 py-2 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all duration-200"
            >
              <Settings className="w-5 h-5" />
              <span className="font-medium">Settings</span>
            </Link>
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
      <div className="flex-1 lg:ml-0">
        {/* Header */}
        <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-30">
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
                  <p className="text-xs text-slate-500 dark:text-slate-400">Faculty</p>
                </div>
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                  <Shield className="w-4 h-4 text-white" />
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8 min-h-[calc(100vh-4rem)]">
          {children}
        </main>
      </div>
    </div>
  );
} 