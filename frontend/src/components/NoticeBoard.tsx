'use client'

import { useState, useEffect } from 'react'
import { 
  Bell, 
  Search, 
  Plus,
  Edit,
  Trash2,
  Eye,
  Tag,
  AlertCircle,
  Info,
  CheckCircle,
  Clock,
  XCircle,
  FileText
} from 'lucide-react'
import { format, isAfter, isBefore } from 'date-fns'

interface Notice {
  id: string
  title: string
  content: string
  type: 'announcement' | 'reminder' | 'urgent' | 'general'
  priority: 'low' | 'medium' | 'high'
  targetAudience?: 'all' | 'students' | 'faculty' | 'specific_course'
  course?: string
  author: string
  authorId: string
  createdAt: string
  updatedAt?: string
  expiresAt?: string
  isActive: boolean
  attachments?: string[]
  readBy?: string[]
  tags?: string[]
}

interface NoticeStats {
  totalNotices: number
  activeNotices: number
  urgentNotices: number
  expiredNotices: number
}

export default function NoticeBoard() {
  const [notices, setNotices] = useState<Notice[]>([])
  const [filteredNotices, setFilteredNotices] = useState<Notice[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [audienceFilter, setAudienceFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [selectedNotice, setSelectedNotice] = useState<Notice | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingNotice, setEditingNotice] = useState<Notice | null>(null)

  const noticeTypes = ['all', 'announcement', 'reminder', 'urgent', 'general']
  const priorities = ['all', 'low', 'medium', 'high']
  const audiences = ['all', 'all', 'students', 'faculty', 'specific_course']

  useEffect(() => {
    loadNotices()
  }, [])

  const loadNotices = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/notices')
      const data = await response.json()
      if (data.success) {
        setNotices(data.data)
        setFilteredNotices(data.data)
      }
    } catch (error) {
      console.error('Error loading notices:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let filtered = notices

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(notice =>
        notice.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        notice.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (notice.tags && notice.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
      )
    }

    // Filter by type
    if (typeFilter !== 'all') {
      filtered = filtered.filter(notice => notice.type === typeFilter)
    }

    // Filter by priority
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(notice => notice.priority === priorityFilter)
    }

    // Filter by audience
    if (audienceFilter !== 'all') {
      filtered = filtered.filter(notice => notice.targetAudience === audienceFilter)
    }

    setFilteredNotices(filtered)
  }, [notices, searchTerm, typeFilter, priorityFilter, audienceFilter])

  const getNoticeStats = (): NoticeStats => {
    const totalNotices = notices.length
    const activeNotices = notices.filter(n => n.isActive).length
    const urgentNotices = notices.filter(n => n.priority === 'high' && n.isActive).length
    const expiredNotices = notices.filter(n => n.expiresAt && isAfter(new Date(), new Date(n.expiresAt))).length

    return {
      totalNotices,
      activeNotices,
      urgentNotices,
      expiredNotices
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'announcement': return <Bell className="h-4 w-4" />
      case 'reminder': return <Clock className="h-4 w-4" />
      case 'urgent': return <AlertCircle className="h-4 w-4" />
      case 'general': return <Info className="h-4 w-4" />
      default: return <Bell className="h-4 w-4" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'announcement': return 'bg-blue-100 text-blue-800'
      case 'reminder': return 'bg-yellow-100 text-yellow-800'
      case 'urgent': return 'bg-red-100 text-red-800'
      case 'general': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const isExpired = (notice: Notice) => {
    return notice.expiresAt && isAfter(new Date(), new Date(notice.expiresAt))
  }

  const isExpiringSoon = (notice: Notice) => {
    if (!notice.expiresAt) return false
    const threeDaysFromNow = new Date()
    threeDaysFromNow.setDate(threeDaysFromNow.getDate() + 3)
    return isBefore(new Date(notice.expiresAt), threeDaysFromNow) && !isExpired(notice)
  }

  const stats = getNoticeStats()

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Notice Board</h2>
          <p className="text-gray-600">Manage announcements and important notices</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>Create Notice</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Notices</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalNotices}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Bell className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Notices</p>
              <p className="text-2xl font-bold text-green-600">{stats.activeNotices}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Urgent Notices</p>
              <p className="text-2xl font-bold text-red-600">{stats.urgentNotices}</p>
            </div>
            <div className="bg-red-100 p-3 rounded-full">
              <AlertCircle className="h-6 w-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Expired Notices</p>
              <p className="text-2xl font-bold text-gray-600">{stats.expiredNotices}</p>
            </div>
            <div className="bg-gray-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-gray-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search notices..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex space-x-3">
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {noticeTypes.map(type => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {priorities.map(priority => (
                <option key={priority} value={priority}>
                  {priority === 'all' ? 'All Priorities' : priority.charAt(0).toUpperCase() + priority.slice(1)}
                </option>
              ))}
            </select>
            <select
              value={audienceFilter}
              onChange={(e) => setAudienceFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {audiences.map(audience => (
                <option key={audience} value={audience}>
                  {audience === 'all' ? 'All Audiences' : audience.charAt(0).toUpperCase() + audience.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Notices List */}
      <div className="space-y-4">
        {filteredNotices.map((notice) => (
          <div key={notice.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="bg-gray-100 p-2 rounded-full">
                      {getTypeIcon(notice.type)}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{notice.title}</h3>
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <span>By {notice.author}</span>
                        <span>•</span>
                        <span>{format(new Date(notice.createdAt), 'MMM d, yyyy • h:mm a')}</span>
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-gray-700 mb-4 line-clamp-2">{notice.content}</p>
                  
                  <div className="flex items-center space-x-4 mb-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(notice.type)}`}>
                      {notice.type.charAt(0).toUpperCase() + notice.type.slice(1)}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(notice.priority)}`}>
                      {notice.priority.charAt(0).toUpperCase() + notice.priority.slice(1)} Priority
                    </span>
                    {notice.targetAudience && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        {notice.targetAudience === 'specific_course' ? 'Course Specific' : notice.targetAudience.charAt(0).toUpperCase() + notice.targetAudience.slice(1)}
                      </span>
                    )}
                    {notice.course && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        {notice.course}
                      </span>
                    )}
                    {isExpired(notice) && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Expired
                      </span>
                    )}
                    {isExpiringSoon(notice) && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        Expiring Soon
                      </span>
                    )}
                  </div>
                  
                  {notice.tags && notice.tags.length > 0 && (
                    <div className="flex items-center space-x-2 mb-4">
                      <Tag className="h-4 w-4 text-gray-400" />
                      <div className="flex flex-wrap gap-1">
                        {notice.tags.map((tag, index) => (
                          <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Read by {notice.readBy ? notice.readBy.length : 0} people</span>
                    {notice.expiresAt && (
                      <span>
                        Expires: {format(new Date(notice.expiresAt), 'MMM d, yyyy')}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2 ml-4">
                  <button
                    onClick={() => setSelectedNotice(notice)}
                    className="flex items-center space-x-1 px-3 py-1 text-blue-600 hover:text-blue-800 text-sm"
                  >
                    <Eye className="h-4 w-4" />
                    <span>View</span>
                  </button>
                  <button
                    onClick={() => {
                      setEditingNotice(notice)
                      setShowEditModal(true)
                    }}
                    className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800 text-sm"
                  >
                    <Edit className="h-4 w-4" />
                    <span>Edit</span>
                  </button>
                  <button className="flex items-center space-x-1 px-3 py-1 text-red-600 hover:text-red-800 text-sm">
                    <Trash2 className="h-4 w-4" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Notice Details Modal */}
      {selectedNotice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedNotice.title}</h3>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                    <span>By {selectedNotice.author}</span>
                    <span>•</span>
                    <span>Created: {format(new Date(selectedNotice.createdAt), 'MMM d, yyyy • h:mm a')}</span>
                    {selectedNotice.updatedAt && selectedNotice.updatedAt !== selectedNotice.createdAt && (
                      <>
                        <span>•</span>
                        <span>Updated: {format(new Date(selectedNotice.updatedAt), 'MMM d, yyyy • h:mm a')}</span>
                      </>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedNotice(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="flex items-center space-x-4 mb-6">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(selectedNotice.type)}`}>
                  {getTypeIcon(selectedNotice.type)}
                  <span className="ml-1">{selectedNotice.type.charAt(0).toUpperCase() + selectedNotice.type.slice(1)}</span>
                </span>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(selectedNotice.priority)}`}>
                  {selectedNotice.priority.charAt(0).toUpperCase() + selectedNotice.priority.slice(1)} Priority
                </span>
                {selectedNotice.targetAudience && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                    {selectedNotice.targetAudience === 'specific_course' ? 'Course Specific' : selectedNotice.targetAudience.charAt(0).toUpperCase() + selectedNotice.targetAudience.slice(1)}
                  </span>
                )}
                {selectedNotice.course && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                    {selectedNotice.course}
                  </span>
                )}
              </div>
              
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap">{selectedNotice.content}</p>
              </div>
              
              {selectedNotice.attachments && selectedNotice.attachments.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2">Attachments</h4>
                  <div className="space-y-2">
                    {selectedNotice.attachments.map((attachment, index) => (
                      <div key={index} className="flex items-center space-x-2 p-2 bg-gray-50 rounded">
                        <FileText className="h-4 w-4 text-gray-400" />
                        <span className="text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
                          {attachment}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedNotice.tags && selectedNotice.tags.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-2">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedNotice.tags.map((tag, index) => (
                      <span key={index} className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-sm">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
