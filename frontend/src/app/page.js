'use client'

import { useState } from 'react'
import { 
  MessageSquare, 
  Users, 
  Calendar, 
  Bell, 
  BarChart3, 
  Settings,
  GraduationCap,
  FileText,
  ExternalLink,
  FolderOpen,
  Briefcase
} from 'lucide-react'
import ChatInterface from '../components/ChatInterface'
import AttendanceViewer from '../components/AttendanceViewer'
import LeaveManagement from '../components/LeaveManagement'
import NoticeBoard from '../components/NoticeBoard'
import Dashboard from '../components/Dashboard'
import QuestionPaperRedirect from '../components/QuestionPaperRedirect'
import Resources from '../components/Resources'
import Placements from '../components/Placements'

const tabs = [
  { id: 'dashboard', name: 'Dashboard', icon: BarChart3, component: Dashboard },
  { id: 'chat', name: 'AI Assistant', icon: MessageSquare, component: ChatInterface },
  { id: 'attendance', name: 'Attendance', icon: Users, component: AttendanceViewer },
  { id: 'leave', name: 'Leave Management', icon: Calendar, component: LeaveManagement },
  { id: 'notices', name: 'Notice Board', icon: Bell, component: NoticeBoard },
  { id: 'question-paper', name: 'Question Papers', icon: FileText, component: QuestionPaperRedirect },
  { id: 'resources', name: 'Resources', icon: FolderOpen, component: Resources },
  { id: 'placements', name: 'Placements', icon: Briefcase, component: Placements },
  { id: 'settings', name: 'Settings', icon: Settings, component: Dashboard },
]

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard')

  const ActiveComponent = tabs.find(tab => tab.id === activeTab)?.component || Dashboard

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <GraduationCap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Academic Management System</h1>
                <p className="text-sm text-gray-500">Faculty Portal</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Dr. Sarah Johnson</p>
                <p className="text-xs text-gray-500">Computer Science Department</p>
              </div>
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-blue-600">SJ</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <ActiveComponent />
      </main>
    </div>
  )
}
