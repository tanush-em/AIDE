'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Clock, 
  BookOpen, 
  Users, 
  Bell, 
  TrendingUp,
  FileText,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  MessageSquare,
  Sparkles,
  GraduationCap,
  Award
} from 'lucide-react';

export default function DashboardPage({ params }) {
  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { role } = params;

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      const userObj = JSON.parse(userData);
      setUser(userObj);
      fetchDashboardData(userObj.id, userObj.role);
    }
  }, [role]);

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

  const getRoleColor = (role) => {
    switch (role) {
      case 'student': return 'from-blue-500 to-cyan-500';
      case 'faculty': return 'from-purple-500 to-pink-500';
      case 'coordinator': return 'from-green-500 to-emerald-500';
      default: return 'from-blue-500 to-purple-500';
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'student': return GraduationCap;
      case 'faculty': return Users;
      case 'coordinator': return Award;
      default: return Sparkles;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!user) {
    return <div>User not found</div>;
  }

  const RoleIcon = getRoleIcon(user.role);

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-slate-50 to-blue-50 dark:from-slate-800 dark:to-slate-700 rounded-2xl p-6 border border-slate-200 dark:border-slate-600"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 dark:text-slate-200 mb-2">
              {getGreeting()}, {user.name}! 👋
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Welcome to your {user.role} dashboard. Here's what's happening today.
            </p>
          </div>
          <div className={`w-16 h-16 rounded-2xl bg-gradient-to-r ${getRoleColor(user.role)} flex items-center justify-center`}>
            <RoleIcon className="w-8 h-8 text-white" />
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
        {role === 'student' && (
          <>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Attendance</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {dashboardData?.attendance?.percentage || 85}%
                  </p>
                </div>
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Today's Classes</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {dashboardData?.timetable?.length || 3}
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
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Pending Tasks</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {dashboardData?.pending_actions?.length || 2}
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
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Notifications</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {dashboardData?.notifications?.length || 2}
                  </p>
                </div>
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                  <Bell className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </div>
          </>
        )}

        {role === 'faculty' && (
          <>
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
          </>
        )}

        {role === 'coordinator' && (
          <>
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Upcoming Events</p>
                  <p className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                    {dashboardData?.upcoming_events?.length || 2}
                  </p>
                </div>
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-blue-600" />
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
          </>
        )}
      </motion.div>

      {/* Main Content Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Role-specific content */}
          {role === 'student' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
            >
              <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Today's Schedule
              </h2>
              <div className="space-y-3">
                {dashboardData?.timetable?.map((class_, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{class_.subject}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{class_.room}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-slate-800 dark:text-slate-200">{class_.time}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{class_.day}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {role === 'faculty' && (
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
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{class_.subject}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{class_.room}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-slate-800 dark:text-slate-200">{class_.time}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{class_.students} students</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {role === 'coordinator' && (
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
                  <div key={index} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{event.name}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">{event.date}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-slate-800 dark:text-slate-200">{event.registrations}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">registrations</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {/* AI Assistant Widget */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-6 text-white"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <MessageSquare className="w-5 h-5 mr-2" />
                AI Assistant
              </h2>
              <Sparkles className="w-5 h-5" />
            </div>
            <p className="text-blue-100 mb-4">
              Get instant help with your academic questions, assignments, and more.
            </p>
            <button className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg font-medium transition-all duration-200">
              Ask a Question
            </button>
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Notifications */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700"
          >
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <Bell className="w-5 h-5 mr-2" />
              Recent Notifications
            </h2>
            <div className="space-y-3">
              {(dashboardData?.notifications || dashboardData?.system_notifications || []).map((notification, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
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
              {role === 'student' && (
                <>
                  <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-5 h-5 text-blue-600" />
                      <span className="text-slate-700 dark:text-slate-300">Submit Leave Application</span>
                    </div>
                  </button>
                  <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <div className="flex items-center space-x-3">
                      <BookOpen className="w-5 h-5 text-green-600" />
                      <span className="text-slate-700 dark:text-slate-300">View Study Materials</span>
                    </div>
                  </button>
                </>
              )}
              
              {role === 'faculty' && (
                <>
                  <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <div className="flex items-center space-x-3">
                      <FileText className="w-5 h-5 text-blue-600" />
                      <span className="text-slate-700 dark:text-slate-300">Upload Resources</span>
                    </div>
                  </button>
                  <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <div className="flex items-center space-x-3">
                      <BarChart3 className="w-5 h-5 text-green-600" />
                      <span className="text-slate-700 dark:text-slate-300">Take Attendance</span>
                    </div>
                  </button>
                </>
              )}

              {role === 'coordinator' && (
                <>
                  <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <div className="flex items-center space-x-3">
                      <Calendar className="w-5 h-5 text-blue-600" />
                      <span className="text-slate-700 dark:text-slate-300">Create Event</span>
                    </div>
                  </button>
                  <button className="w-full text-left p-3 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-lg transition-colors">
                    <div className="flex items-center space-x-3">
                      <Bell className="w-5 h-5 text-green-600" />
                      <span className="text-slate-700 dark:text-slate-300">Send Notification</span>
                    </div>
                  </button>
                </>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
} 