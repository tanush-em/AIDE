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
  GraduationCap,
  Clock3,
  MapPin,
  Users,
  Home,
  CalendarDays,
  BookOpen as BookOpenIcon,
  BarChart3 as BarChart3Icon,
  MessageSquare as MessageSquareIcon,
  Settings
} from 'lucide-react';
import NoticeBoard from '../../../components/NoticeBoard';

export default function StudentDashboard() {
  const [user, setUser] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('notices');

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
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
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
        className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-800"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-800 dark:text-slate-200 mb-2">
              {getGreeting()}, {user.name}! 👋
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Welcome to your student dashboard. Here's what's happening today.
            </p>
          </div>
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 flex items-center justify-center">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6"
      >
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
      </motion.div>

      {/* Tab Navigation */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden"
      >
        <div className="flex border-b border-slate-200 dark:border-slate-700">
          {[
            { id: 'notices', label: 'Notice Board', icon: Bell },
            { id: 'schedule', label: 'Schedule', icon: CalendarDays },
            { id: 'resources', label: 'Resources', icon: BookOpenIcon },
            { id: 'attendance', label: 'Attendance', icon: BarChart3Icon },
            { id: 'assistant', label: 'AI Assistant', icon: MessageSquareIcon },
            { id: 'quick-actions', label: 'Quick Actions', icon: Settings }
          ].map((tab) => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700'
                }`}
              >
                <IconComponent className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </motion.div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="min-h-[600px]"
      >
        {activeTab === 'notices' && <NoticeBoard />}
        
        {activeTab === 'schedule' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2" />
              Today's Schedule
            </h2>
            <div className="space-y-3">
              {dashboardData?.timetable?.map((class_, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                      <Clock3 className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-800 dark:text-slate-200">{class_.subject}</p>
                      <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                        <MapPin className="w-4 h-4" />
                        <span>{class_.room}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-slate-800 dark:text-slate-200">{class_.time}</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400">{class_.day}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'resources' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <BookOpen className="w-5 h-5 mr-2" />
              Study Resources
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                <div className="flex items-center space-x-3 mb-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <h3 className="font-medium text-slate-800 dark:text-slate-200">Mathematics Notes</h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">Comprehensive notes for Calculus and Linear Algebra</p>
                <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View Notes</button>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                <div className="flex items-center space-x-3 mb-3">
                  <FileText className="w-5 h-5 text-green-600" />
                  <h3 className="font-medium text-slate-800 dark:text-slate-200">Physics Lab Manual</h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">Lab procedures and experiment guidelines</p>
                <button className="text-green-600 hover:text-green-700 text-sm font-medium">Download</button>
              </div>
              <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600">
                <div className="flex items-center space-x-3 mb-3">
                  <FileText className="w-5 h-5 text-purple-600" />
                  <h3 className="font-medium text-slate-800 dark:text-slate-200">Chemistry Formulas</h3>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">Quick reference for chemical formulas</p>
                <button className="text-purple-600 hover:text-purple-700 text-sm font-medium">View Sheet</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'attendance' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Attendance Overview
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                <div className="text-3xl font-bold text-blue-600 mb-2">{dashboardData?.attendance?.percentage || 85}%</div>
                <div className="text-sm text-slate-600 dark:text-slate-400">Overall Attendance</div>
              </div>
              <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                <div className="text-3xl font-bold text-green-600 mb-2">{dashboardData?.attendance?.present || 85}</div>
                <div className="text-sm text-slate-600 dark:text-slate-400">Classes Attended</div>
              </div>
              <div className="text-center p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                <div className="text-3xl font-bold text-orange-600 mb-2">{dashboardData?.attendance?.total - dashboardData?.attendance?.present || 15}</div>
                <div className="text-sm text-slate-600 dark:text-slate-400">Classes Missed</div>
              </div>
            </div>
            <div className="space-y-3">
              <h3 className="font-medium text-slate-800 dark:text-slate-200 mb-3">Subject-wise Attendance</h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <span className="text-slate-800 dark:text-slate-200">Mathematics</span>
                  <span className="text-green-600 font-medium">92%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <span className="text-slate-800 dark:text-slate-200">Physics</span>
                  <span className="text-orange-600 font-medium">78%</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
                  <span className="text-slate-800 dark:text-slate-200">Chemistry</span>
                  <span className="text-green-600 font-medium">88%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'assistant' && (
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-8 text-white">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold flex items-center">
                <MessageSquare className="w-6 h-6 mr-3" />
                AI Study Assistant
              </h2>
              <Sparkles className="w-6 h-6" />
            </div>
            <p className="text-blue-100 mb-6 text-lg">
              Get instant help with your studies, assignments, and academic questions. Our AI assistant is here to support your learning journey.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-white/20 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Quick Questions</h3>
                <p className="text-blue-100 text-sm">Ask about concepts, formulas, or get homework help</p>
              </div>
              <div className="bg-white/20 rounded-lg p-4">
                <h3 className="font-semibold mb-2">Study Planning</h3>
                <p className="text-blue-100 text-sm">Get personalized study schedules and tips</p>
              </div>
            </div>
            <button className="bg-white/20 hover:bg-white/30 px-6 py-3 rounded-lg font-medium transition-all duration-200 text-lg">
              Start Chat with AI Assistant
            </button>
          </div>
        )}

        {activeTab === 'quick-actions' && (
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200 mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Quick Actions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <button className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors text-left">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <span className="text-slate-700 dark:text-slate-300">Submit Leave Application</span>
                </div>
              </button>
              <button className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors text-left">
                <div className="flex items-center space-x-3">
                  <BookOpen className="w-5 h-5 text-green-600" />
                  <span className="text-slate-700 dark:text-slate-300">View Study Materials</span>
                </div>
              </button>
              <button className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors text-left">
                <div className="flex items-center space-x-3">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  <span className="text-slate-700 dark:text-slate-300">Check Attendance</span>
                </div>
              </button>
              <button className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors text-left">
                <div className="flex items-center space-x-3">
                  <Calendar className="w-5 h-5 text-orange-600" />
                  <span className="text-slate-700 dark:text-slate-300">View Timetable</span>
                </div>
              </button>
              <button className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors text-left">
                <div className="flex items-center space-x-3">
                  <Bell className="w-5 h-5 text-red-600" />
                  <span className="text-slate-700 dark:text-slate-300">Notifications</span>
                </div>
              </button>
              <button className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors text-left">
                <div className="flex items-center space-x-3">
                  <MessageSquare className="w-5 h-5 text-indigo-600" />
                  <span className="text-slate-700 dark:text-slate-300">Contact Support</span>
                </div>
              </button>
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
} 