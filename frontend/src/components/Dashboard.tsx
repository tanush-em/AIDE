'use client'

import { useState, useEffect } from 'react'
import { 
  Users, 
  Calendar, 
  Bell, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertCircle,
  BookOpen,
  FileText,
  ExternalLink
} from 'lucide-react'
import { format } from 'date-fns'

interface DashboardStats {
  totalStudents: number
  attendanceRate: number
  pendingLeaves: number
  upcomingEvents: number
  recentActivities: Activity[]
}

interface Activity {
  id: string
  type: 'attendance' | 'leave' | 'notice' | 'grade'
  title: string
  description: string
  timestamp: Date
  status: 'completed' | 'pending' | 'overdue'
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    totalStudents: 0,
    attendanceRate: 0,
    pendingLeaves: 0,
    upcomingEvents: 0,
    recentActivities: []
  })
  const [loading, setLoading] = useState(true)

  const handleQuickAction = (action: string) => {
    switch (action) {
      case 'attendance':
        // Navigate to attendance tab
        window.location.hash = '#attendance'
        break
      case 'leaves':
        // Navigate to leave management tab
        window.location.hash = '#leave'
        break
      case 'notice':
        // Navigate to notice board tab
        window.location.hash = '#notices'
        break
      default:
        break
    }
  }

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setStats({
        totalStudents: 156,
        attendanceRate: 87.5,
        pendingLeaves: 8,
        upcomingEvents: 3,
        recentActivities: [
          {
            id: '1',
            type: 'attendance',
            title: 'CS101 - Data Structures',
            description: 'Attendance marked for 45/50 students',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
            status: 'completed'
          },
          {
            id: '2',
            type: 'leave',
            title: 'Leave Request - John Smith',
            description: 'Sick leave for 3 days pending approval',
            timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
            status: 'pending'
          },
          {
            id: '3',
            type: 'notice',
            title: 'Mid-term Exam Schedule',
            description: 'Exam schedule published for all courses',
            timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
            status: 'completed'
          },
          {
            id: '4',
            type: 'grade',
            title: 'Assignment Grades Due',
            description: 'CS201 Assignment 2 grades due tomorrow',
            timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000), // 8 hours ago
            status: 'overdue'
          }
        ]
      })
      setLoading(false)
    }, 1000)
  }, [])

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'attendance': return <Users className="h-4 w-4" />
      case 'leave': return <Calendar className="h-4 w-4" />
      case 'notice': return <Bell className="h-4 w-4" />
      case 'grade': return <BookOpen className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100'
      case 'pending': return 'text-yellow-600 bg-yellow-100'
      case 'overdue': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">Welcome back, Dr. Sarah Johnson!</h2>
        <p className="text-blue-100">Here&apos;s what&apos;s happening in your academic management today.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Students</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalStudents}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>+5% from last month</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Attendance Rate</p>
              <p className="text-2xl font-bold text-gray-900">{stats.attendanceRate}%</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-green-600">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>+2.3% from last week</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Leaves</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pendingLeaves}</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <AlertCircle className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-yellow-600">
            <Clock className="h-4 w-4 mr-1" />
            <span>Requires attention</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Upcoming Events</p>
              <p className="text-2xl font-bold text-gray-900">{stats.upcomingEvents}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm text-purple-600">
            <Calendar className="h-4 w-4 mr-1" />
            <span>This week</span>
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Recent Activities</h3>
          <p className="text-sm text-gray-600">Latest updates from your academic management</p>
        </div>
        <div className="divide-y">
          {stats.recentActivities.map((activity) => (
            <div key={activity.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="bg-gray-100 p-2 rounded-full">
                    {getActivityIcon(activity.type)}
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                      {activity.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{activity.description}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    {format(activity.timestamp, 'MMM d, yyyy • h:mm a')}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button 
            onClick={() => handleQuickAction('attendance')}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="bg-blue-100 p-2 rounded-full">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Mark Attendance</p>
              <p className="text-sm text-gray-600">Record today&apos;s attendance</p>
            </div>
          </button>
          
          <button 
            onClick={() => handleQuickAction('leaves')}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="bg-green-100 p-2 rounded-full">
              <Calendar className="h-5 w-5 text-green-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Review Leaves</p>
              <p className="text-sm text-gray-600">Approve pending requests</p>
            </div>
          </button>
          
          <button 
            onClick={() => handleQuickAction('notice')}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="bg-purple-100 p-2 rounded-full">
              <Bell className="h-5 w-5 text-purple-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Post Notice</p>
              <p className="text-sm text-gray-600">Create new announcement</p>
            </div>
          </button>

          <button 
            onClick={() => window.open('http://localhost:5890', '_blank')}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="bg-orange-100 p-2 rounded-full">
              <FileText className="h-5 w-5 text-orange-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Question Papers</p>
              <p className="text-sm text-gray-600">Generate exam papers</p>
            </div>
            <ExternalLink className="h-4 w-4 text-gray-400" />
          </button>
        </div>
      </div>
    </div>
  )
}
