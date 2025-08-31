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
  Award,
  Clock3,
  MapPin,
  Users,
  Event,
  UserPlus
} from 'lucide-react';

export default function CoordinatorDashboard() {
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
        <div className="w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full animate-spin"></div>
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
        className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-2xl p-6 border border-green-200 dark:border-green-800"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 dark:text-slate-200 mb-2">
              {getGreeting()}, {user.name}! 👋
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Welcome to your coordinator dashboard. Here's what's happening today.
            </p>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center">
            <Award className="w-8 h-8 text-white" />
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
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Upcoming Events</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {dashboardData?.upcoming_events?.length || 2}
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <Event className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Total Registrations</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">239</p>
            </div>
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">System Alerts</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                {dashboardData?.system_notifications?.length || 2}
              </p>
            </div>
            <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Reports</p>
              <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">8</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Content Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Upcoming Events */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Upcoming Events
            </h2>
            <div className="space-y-3">
              {dashboardData?.upcoming_events?.map((event, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                      <Event className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{event.name}</p>
                      <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                        <Calendar className="w-4 h-4" />
                        <span>{event.date}</span>
                        <span>•</span>
                        <span>{event.registrations} registrations</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <button className="text-sm text-green-600 hover:text-green-700 font-medium">
                      Manage Event
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* System Notifications */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              System Notifications
            </h2>
            <div className="space-y-3">
              {(dashboardData?.system_notifications || []).map((notification, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    notification.type === 'warning' ? 'bg-orange-500' : 'bg-blue-500'
                  }`} />
                  <div className="flex-1">
                    <p className="text-sm text-slate-800 dark:text-slate-200">{notification.message}</p>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{notification.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* AI Assistant Widget */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-6 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                AI Management Assistant
              </h2>
              <Sparkles className="w-5 h-5" />
            </div>
            <p className="text-green-100 mb-4">
              Get help with event management, reports, and administrative tasks.
            </p>
            <button className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-medium transition-all duration-200">
              Ask for Help
            </button>
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4">
              Quick Actions
            </h2>
            <div className="space-y-2">
              <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <Event className="w-5 h-5 text-blue-600" />
                  <span className="text-slate-700 dark:text-slate-300">Create Event</span>
                </div>
              </button>
              <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <Bell className="w-5 h-5 text-green-600" />
                  <span className="text-slate-700 dark:text-slate-300">Send Notification</span>
                </div>
              </button>
              <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  <span className="text-slate-700 dark:text-slate-300">Generate Report</span>
                </div>
              </button>
              <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                <div className="flex items-center space-x-3">
                  <UserPlus className="w-5 h-5 text-orange-600" />
                  <span className="text-slate-700 dark:text-slate-300">Manage Registrations</span>
                </div>
              </button>
            </div>
          </motion.div>

          {/* Recent Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4">
              Recent Activity
            </h2>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 p-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm text-slate-800 dark:text-slate-200">New event created: Tech Fest 2024</p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">2 hours ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm text-slate-800 dark:text-slate-200">50 students registered for Career Fair</p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">4 hours ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3 p-2">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm text-slate-800 dark:text-slate-200">System maintenance scheduled</p>
                  <p className="text-xs text-slate-600 dark:text-slate-400">1 day ago</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
} 