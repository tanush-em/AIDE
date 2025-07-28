'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Clock, 
  BookOpen, 
  Bell, 
  TrendingUp,
  FileText,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  MessageSquare,
  Sparkles,
  Users,
  Clock3,
  MapPin,
  GraduationCap,
  Upload,
  CheckCircle2
} from 'lucide-react';

export default function FacultyDashboard() {
  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const userObj = JSON.parse(userData);
      setUser(userObj);
      fetchDashboardData(userObj.id, userObj.role);
    }
  }, []);

  const fetchDashboardData = async (userId, userRole) => {
    try {
      const response = await fetch(`http://localhost:5001/api/dashboard/${userRole}/${userId}`);
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!user) {
    return <div>User not found</div>;
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl p-6 border border-purple-200 dark:border-purple-800"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 dark:text-slate-200 mb-2">
              {getGreeting()}, {user.name}! 👋
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Welcome to your faculty dashboard. Here's what's happening today.
            </p>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
            <Users className="w-8 h-8 text-white" />
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Today's Classes</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {dashboardData?.classes_today?.length || 2}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Pending Grading</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {dashboardData?.pending_grading?.length || 2}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
              <FileText className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Leave Requests</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {dashboardData?.leave_requests?.length || 1}
              </p>
            </div>
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Resources</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">12</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Content Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Today's Classes */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2" />
              Today's Classes
            </h2>
            <div className="space-y-3">
              {dashboardData?.classes_today?.map((class_, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                      <Clock3 className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{class_.subject}</p>
                      <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                        <MapPin className="w-4 h-4" />
                        <span>{class_.room}</span>
                        <span>•</span>
                        <span>{class_.students} students</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-slate-800 dark:text-slate-200">{class_.time}</p>
                    <button className="text-sm text-purple-600 hover:text-purple-700 font-medium">
                      Take Attendance
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Pending Grading */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <FileText className="w-5 h-5 mr-2" />
              Pending Grading
            </h2>
            <div className="space-y-3">
              {dashboardData?.pending_grading?.map((assignment, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                      <FileText className="w-5 h-5 text-orange-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{assignment.assignment}</p>
                      <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                        <span>{assignment.submissions} submissions</span>
                        <span>•</span>
                        <span>Due: {assignment.due}</span>
                      </div>
                    </div>
                  </div>
                  <button className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors">
                    Grade Now
                  </button>
                </div>
              ))}
            </div>
          </motion.div>

          {/* AI Assistant Widget */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl p-6 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                AI Teaching Assistant
              </h2>
              <Sparkles className="w-5 h-5" />
            </div>
            <p className="text-purple-100 mb-4">
              Get help with grading, question generation, and teaching resources.
            </p>
            <button className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-medium transition-all duration-200">
              Ask for Help
            </button>
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Leave Requests */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Leave Requests
            </h2>
            <div className="space-y-3">
              {(dashboardData?.leave_requests || []).map((request, index) => (
                <div key={index} className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                  <div className="flex items-start justify-between mb-2">
                    <p className="font-medium text-slate-800 dark:text-slate-200">{request.student}</p>
                    <span className="text-xs text-slate-500 dark:text-slate-400">{request.dates}</span>
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">{request.reason}</p>
                  <div className="flex space-x-2">
                    <button className="flex-1 px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-sm rounded-lg transition-colors">
                      Approve
                    </button>
                    <button className="flex-1 px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors">
                      Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4">
              Quick Actions
            </h2>
            <div className="space-y-2">
              <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <Upload className="w-5 h-5 text-blue-600" />
                  <span className="text-slate-700 dark:text-slate-300">Upload Resources</span>
                </div>
              </button>
              <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-green-600" />
                  <span className="text-slate-700 dark:text-slate-300">Generate Question Paper</span>
                </div>
              </button>
              <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  <span className="text-slate-700 dark:text-slate-300">View Attendance</span>
                </div>
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
} 