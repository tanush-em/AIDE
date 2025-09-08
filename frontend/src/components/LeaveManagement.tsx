'use client'

import { useState, useEffect } from 'react'
import { 
  Search, 
  Plus,
  CheckCircle,
  XCircle,
  Clock,
  User,
  FileText,
  TrendingUp
} from 'lucide-react'
import { format, differenceInDays } from 'date-fns'

interface LeaveRequest {
  id: string
  studentId: string
  studentName: string
  studentRollNumber: string
  course: string
  leaveType: 'sick' | 'personal' | 'emergency' | 'academic'
  startDate: string
  endDate: string
  duration: number
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  submittedAt: string
  reviewedAt?: string
  reviewedBy?: string
  remarks?: string
  attachments?: string[]
}

interface LeaveStats {
  totalRequests: number
  pendingRequests: number
  approvedRequests: number
  rejectedRequests: number
  averageProcessingTime: number
}

export default function LeaveManagement() {
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([])
  const [filteredRequests, setFilteredRequests] = useState<LeaveRequest[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [leaveTypeFilter, setLeaveTypeFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [selectedRequest, setSelectedRequest] = useState<LeaveRequest | null>(null)
  const [showApprovalModal, setShowApprovalModal] = useState(false)
  const [approvalAction, setApprovalAction] = useState<'approve' | 'reject'>('approve')
  const [remarks, setRemarks] = useState('')

  const leaveTypes = ['all', 'sick', 'personal', 'emergency', 'academic']
  const statuses = ['all', 'pending', 'approved', 'rejected']

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const mockRequests: LeaveRequest[] = [
        {
          id: '1',
          studentId: 'STU001',
          studentName: 'Alice Johnson',
          studentRollNumber: 'CS001',
          course: 'CS101',
          leaveType: 'sick',
          startDate: '2024-01-20',
          endDate: '2024-01-22',
          duration: 3,
          reason: 'Fever and flu symptoms. Doctor recommended rest.',
          status: 'pending',
          submittedAt: '2024-01-19T10:30:00Z',
          attachments: ['medical_certificate.pdf']
        },
        {
          id: '2',
          studentId: 'STU002',
          studentName: 'Bob Smith',
          studentRollNumber: 'CS002',
          course: 'CS101',
          leaveType: 'personal',
          startDate: '2024-01-25',
          endDate: '2024-01-25',
          duration: 1,
          reason: 'Family emergency - need to attend to urgent matter.',
          status: 'pending',
          submittedAt: '2024-01-24T14:20:00Z'
        },
        {
          id: '3',
          studentId: 'STU003',
          studentName: 'Carol Davis',
          studentRollNumber: 'CS003',
          course: 'CS201',
          leaveType: 'academic',
          startDate: '2024-01-18',
          endDate: '2024-01-18',
          duration: 1,
          reason: 'Attending academic conference for research presentation.',
          status: 'approved',
          submittedAt: '2024-01-15T09:15:00Z',
          reviewedAt: '2024-01-16T11:30:00Z',
          reviewedBy: 'Dr. Sarah Johnson',
          remarks: 'Approved for academic development.'
        },
        {
          id: '4',
          studentId: 'STU004',
          studentName: 'David Wilson',
          studentRollNumber: 'CS004',
          course: 'CS201',
          leaveType: 'personal',
          startDate: '2024-01-12',
          endDate: '2024-01-15',
          duration: 4,
          reason: 'Personal family event.',
          status: 'rejected',
          submittedAt: '2024-01-10T16:45:00Z',
          reviewedAt: '2024-01-11T10:20:00Z',
          reviewedBy: 'Dr. Sarah Johnson',
          remarks: 'Duration too long for personal leave. Please provide more details.'
        }
      ]
      setLeaveRequests(mockRequests)
      setFilteredRequests(mockRequests)
      setLoading(false)
    }, 1000)
  }, [])

  useEffect(() => {
    let filtered = leaveRequests

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(request =>
        request.studentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        request.studentRollNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
        request.course.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(request => request.status === statusFilter)
    }

    // Filter by leave type
    if (leaveTypeFilter !== 'all') {
      filtered = filtered.filter(request => request.leaveType === leaveTypeFilter)
    }

    setFilteredRequests(filtered)
  }, [leaveRequests, searchTerm, statusFilter, leaveTypeFilter])

  const getLeaveStats = (): LeaveStats => {
    const totalRequests = leaveRequests.length
    const pendingRequests = leaveRequests.filter(r => r.status === 'pending').length
    const approvedRequests = leaveRequests.filter(r => r.status === 'approved').length
    const rejectedRequests = leaveRequests.filter(r => r.status === 'rejected').length
    
    const processedRequests = leaveRequests.filter(r => r.reviewedAt)
    const averageProcessingTime = processedRequests.length > 0 
      ? processedRequests.reduce((acc, r) => {
          const submitted = new Date(r.submittedAt)
          const reviewed = new Date(r.reviewedAt!)
          return acc + differenceInDays(reviewed, submitted)
        }, 0) / processedRequests.length
      : 0

    return {
      totalRequests,
      pendingRequests,
      approvedRequests,
      rejectedRequests,
      averageProcessingTime
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'rejected': return <XCircle className="h-4 w-4 text-red-600" />
      case 'pending': return <Clock className="h-4 w-4 text-yellow-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getLeaveTypeColor = (type: string) => {
    switch (type) {
      case 'sick': return 'bg-red-100 text-red-800'
      case 'personal': return 'bg-blue-100 text-blue-800'
      case 'emergency': return 'bg-orange-100 text-orange-800'
      case 'academic': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleApproval = async (requestId: string, action: 'approve' | 'reject') => {
    // Simulate API call
    setLeaveRequests(prev => prev.map(req => 
      req.id === requestId 
        ? {
            ...req,
            status: action === 'approve' ? 'approved' : 'rejected',
            reviewedAt: new Date().toISOString(),
            reviewedBy: 'Dr. Sarah Johnson',
            remarks: remarks
          }
        : req
    ))
    setShowApprovalModal(false)
    setSelectedRequest(null)
    setRemarks('')
  }

  const stats = getLeaveStats()

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
          <h2 className="text-2xl font-bold text-gray-900">Leave Management</h2>
          <p className="text-gray-600">Review and manage student leave requests</p>
        </div>
        <div className="flex space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="h-4 w-4" />
            <span>New Policy</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Requests</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalRequests}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.pendingRequests}</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-green-600">{stats.approvedRequests}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg. Processing</p>
              <p className="text-2xl font-bold text-gray-900">{stats.averageProcessingTime.toFixed(1)} days</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <TrendingUp className="h-6 w-6 text-purple-600" />
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
                placeholder="Search students..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex space-x-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {statuses.map(status => (
                <option key={status} value={status}>
                  {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
                </option>
              ))}
            </select>
            <select
              value={leaveTypeFilter}
              onChange={(e) => setLeaveTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {leaveTypes.map(type => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Leave Requests List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">
            Leave Requests ({filteredRequests.length})
          </h3>
        </div>
        <div className="divide-y">
          {filteredRequests.map((request) => (
            <div key={request.id} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="bg-gray-100 p-2 rounded-full">
                      <User className="h-4 w-4 text-gray-600" />
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900">{request.studentName}</h4>
                      <p className="text-sm text-gray-600">{request.studentRollNumber} • {request.course}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                    <div>
                      <p className="text-sm text-gray-600">Leave Type</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLeaveTypeColor(request.leaveType)}`}>
                        {request.leaveType.charAt(0).toUpperCase() + request.leaveType.slice(1)}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Duration</p>
                      <p className="font-medium">{request.duration} day{request.duration > 1 ? 's' : ''}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Dates</p>
                      <p className="font-medium">
                        {format(new Date(request.startDate), 'MMM d')} - {format(new Date(request.endDate), 'MMM d, yyyy')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-3">
                    <p className="text-sm text-gray-600">Reason</p>
                    <p className="text-sm text-gray-900">{request.reason}</p>
                  </div>
                  
                  {request.attachments && request.attachments.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm text-gray-600">Attachments</p>
                      <div className="flex space-x-2">
                        {request.attachments.map((attachment, index) => (
                          <span key={index} className="text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
                            {attachment}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Submitted: {format(new Date(request.submittedAt), 'MMM d, yyyy • h:mm a')}</span>
                    {request.reviewedAt && (
                      <span>Reviewed: {format(new Date(request.reviewedAt), 'MMM d, yyyy • h:mm a')}</span>
                    )}
                  </div>
                </div>
                
                <div className="flex flex-col items-end space-y-3">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                    {getStatusIcon(request.status)}
                    <span className="ml-1">{request.status.charAt(0).toUpperCase() + request.status.slice(1)}</span>
                  </span>
                  
                  {request.status === 'pending' && (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setSelectedRequest(request)
                          setApprovalAction('approve')
                          setShowApprovalModal(true)
                        }}
                        className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => {
                          setSelectedRequest(request)
                          setApprovalAction('reject')
                          setShowApprovalModal(true)
                        }}
                        className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition-colors"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                  
                  <button
                    onClick={() => setSelectedRequest(request)}
                    className="text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Approval Modal */}
      {showApprovalModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                {approvalAction === 'approve' ? 'Approve' : 'Reject'} Leave Request
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {selectedRequest.studentName} - {selectedRequest.leaveType} leave
              </p>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Remarks
                </label>
                <textarea
                  value={remarks}
                  onChange={(e) => setRemarks(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Add remarks (optional)"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowApprovalModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleApproval(selectedRequest.id, approvalAction)}
                  className={`px-4 py-2 text-white rounded-lg transition-colors ${
                    approvalAction === 'approve' 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {approvalAction === 'approve' ? 'Approve' : 'Reject'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
