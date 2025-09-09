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

export default function LeaveManagement() {
  const [leaveRequests, setLeaveRequests] = useState([])
  const [filteredRequests, setFilteredRequests] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [leaveTypeFilter, setLeaveTypeFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [selectedRequest, setSelectedRequest] = useState(null)
  const [showApprovalModal, setShowApprovalModal] = useState(false)
  const [approvalAction, setApprovalAction] = useState('')

  const statusOptions = ['all', 'pending', 'approved', 'rejected']
  const leaveTypes = ['all', 'sick', 'personal', 'emergency', 'academic']

  useEffect(() => {
    loadLeaveRequests()
  }, [])

  const loadLeaveRequests = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/leave/requests')
      const data = await response.json()
      if (data.success) {
        setLeaveRequests(data.data)
        setFilteredRequests(data.data)
      }
    } catch (error) {
      console.error('Error loading leave requests:', error)
      // Fallback to mock data
      const mockRequests = [
        {
          id: '1',
          studentId: 'STU001',
          studentName: 'John Smith',
          studentRollNumber: 'CS2024001',
          course: 'CS101',
          leaveType: 'sick',
          startDate: '2024-01-20',
          endDate: '2024-01-22',
          duration: 3,
          reason: 'Fever and cold symptoms',
          status: 'pending',
          submittedAt: '2024-01-19T10:00:00Z',
          attachments: ['medical_certificate.pdf']
        },
        {
          id: '2',
          studentId: 'STU002',
          studentName: 'Sarah Johnson',
          studentRollNumber: 'CS2024002',
          course: 'CS201',
          leaveType: 'personal',
          startDate: '2024-01-25',
          endDate: '2024-01-26',
          duration: 2,
          reason: 'Family wedding',
          status: 'approved',
          submittedAt: '2024-01-18T14:30:00Z',
          reviewedAt: '2024-01-19T09:15:00Z',
          reviewedBy: 'Dr. Sarah Johnson',
          remarks: 'Approved for family event'
        },
        {
          id: '3',
          studentId: 'STU003',
          studentName: 'Michael Chen',
          studentRollNumber: 'CS2024003',
          course: 'CS301',
          leaveType: 'emergency',
          startDate: '2024-01-21',
          endDate: '2024-01-21',
          duration: 1,
          reason: 'Medical emergency in family',
          status: 'pending',
          submittedAt: '2024-01-20T16:45:00Z'
        }
      ]
      setLeaveRequests(mockRequests)
      setFilteredRequests(mockRequests)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let filtered = leaveRequests

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(request =>
        request.studentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        request.studentRollNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
        request.reason.toLowerCase().includes(searchTerm.toLowerCase())
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

  const getLeaveStats = () => {
    const totalRequests = leaveRequests.length
    const pendingRequests = leaveRequests.filter(r => r.status === 'pending').length
    const approvedRequests = leaveRequests.filter(r => r.status === 'approved').length
    const rejectedRequests = leaveRequests.filter(r => r.status === 'rejected').length
    const averageProcessingTime = 2.5 // Mock data

    return {
      totalRequests,
      pendingRequests,
      approvedRequests,
      rejectedRequests,
      averageProcessingTime
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800'
      case 'approved': return 'bg-green-100 text-green-800'
      case 'rejected': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />
      case 'approved': return <CheckCircle className="h-4 w-4" />
      case 'rejected': return <XCircle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getLeaveTypeColor = (type) => {
    switch (type) {
      case 'sick': return 'bg-red-100 text-red-800'
      case 'personal': return 'bg-blue-100 text-blue-800'
      case 'emergency': return 'bg-orange-100 text-orange-800'
      case 'academic': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleApproval = async (requestId, action) => {
    try {
      const response = await fetch(`http://localhost:5001/api/leave/requests/${requestId}/${action}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          reviewedBy: 'Dr. Sarah Johnson',
          remarks: action === 'approve' ? 'Request approved' : 'Request rejected'
        }),
      })

      const data = await response.json()
      if (data.success) {
        await loadLeaveRequests()
        setShowApprovalModal(false)
        setSelectedRequest(null)
        alert(`Leave request ${action}d successfully`)
      } else {
        alert(`Failed to ${action} leave request`)
      }
    } catch (error) {
      console.error(`Error ${action}ing leave request:`, error)
      alert(`Failed to ${action} leave request`)
    }
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
          <p className="text-gray-600">Manage student leave requests and approvals</p>
        </div>
        <div className="flex space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <FileText className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="h-4 w-4" />
            <span>Add Request</span>
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
              <p className="text-sm font-medium text-gray-600">Pending Requests</p>
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
              <p className="text-sm font-medium text-gray-600">Approved Requests</p>
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
              <p className="text-sm font-medium text-gray-600">Avg. Processing Time</p>
              <p className="text-2xl font-bold text-purple-600">{stats.averageProcessingTime}d</p>
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
                placeholder="Search students, roll numbers, reasons..."
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
              {statusOptions.map(status => (
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

      {/* Requests List */}
      <div className="space-y-4">
        {filteredRequests.map((request) => (
          <div key={request.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <User className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{request.studentName}</h3>
                      <p className="text-sm text-gray-600">{request.studentRollNumber} • {request.course}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Leave Type</p>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLeaveTypeColor(request.leaveType)}`}>
                        {request.leaveType.charAt(0).toUpperCase() + request.leaveType.slice(1)}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Duration</p>
                      <p className="text-sm text-gray-900">{request.duration} day{request.duration > 1 ? 's' : ''}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Date Range</p>
                      <p className="text-sm text-gray-900">
                        {format(new Date(request.startDate), 'MMM d')} - {format(new Date(request.endDate), 'MMM d, yyyy')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-600 mb-1">Reason</p>
                    <p className="text-sm text-gray-900">{request.reason}</p>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(request.status)}`}>
                      {getStatusIcon(request.status)}
                      <span className="ml-1">{request.status.charAt(0).toUpperCase() + request.status.slice(1)}</span>
                    </span>
                    <span className="text-xs text-gray-500">
                      Submitted: {format(new Date(request.submittedAt), 'MMM d, yyyy • h:mm a')}
                    </span>
                    {request.reviewedAt && (
                      <span className="text-xs text-gray-500">
                        Reviewed: {format(new Date(request.reviewedAt), 'MMM d, yyyy • h:mm a')}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2 ml-4">
                  {request.status === 'pending' && (
                    <>
                      <button
                        onClick={() => {
                          setSelectedRequest(request)
                          setApprovalAction('approve')
                          setShowApprovalModal(true)
                        }}
                        className="flex items-center space-x-1 px-3 py-1 text-green-600 hover:text-green-800 text-sm"
                      >
                        <CheckCircle className="h-4 w-4" />
                        <span>Approve</span>
                      </button>
                      <button
                        onClick={() => {
                          setSelectedRequest(request)
                          setApprovalAction('reject')
                          setShowApprovalModal(true)
                        }}
                        className="flex items-center space-x-1 px-3 py-1 text-red-600 hover:text-red-800 text-sm"
                      >
                        <XCircle className="h-4 w-4" />
                        <span>Reject</span>
                      </button>
                    </>
                  )}
                  <button
                    onClick={() => setSelectedRequest(request)}
                    className="flex items-center space-x-1 px-3 py-1 text-blue-600 hover:text-blue-800 text-sm"
                  >
                    <FileText className="h-4 w-4" />
                    <span>View Details</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Approval Modal */}
      {showApprovalModal && selectedRequest && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                {approvalAction === 'approve' ? 'Approve' : 'Reject'} Leave Request
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Are you sure you want to {approvalAction} the leave request from {selectedRequest.studentName}?
              </p>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowApprovalModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
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

      {/* Request Details Modal */}
      {selectedRequest && !showApprovalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h3 className="text-xl font-semibold text-gray-900">Leave Request Details</h3>
                <button
                  onClick={() => setSelectedRequest(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Student Information</h4>
                  <div className="space-y-1 text-sm">
                    <div><span className="font-medium">Name:</span> {selectedRequest.studentName}</div>
                    <div><span className="font-medium">Roll Number:</span> {selectedRequest.studentRollNumber}</div>
                    <div><span className="font-medium">Course:</span> {selectedRequest.course}</div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Leave Details</h4>
                  <div className="space-y-1 text-sm">
                    <div><span className="font-medium">Type:</span> {selectedRequest.leaveType}</div>
                    <div><span className="font-medium">Duration:</span> {selectedRequest.duration} day{selectedRequest.duration > 1 ? 's' : ''}</div>
                    <div><span className="font-medium">Start Date:</span> {format(new Date(selectedRequest.startDate), 'MMM d, yyyy')}</div>
                    <div><span className="font-medium">End Date:</span> {format(new Date(selectedRequest.endDate), 'MMM d, yyyy')}</div>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Reason</h4>
                <p className="text-sm text-gray-700">{selectedRequest.reason}</p>
              </div>
              {selectedRequest.attachments && selectedRequest.attachments.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Attachments</h4>
                  <div className="space-y-1">
                    {selectedRequest.attachments.map((attachment, index) => (
                      <div key={index} className="text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
                        {attachment}
                      </div>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Status Information</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="font-medium">Status:</span> 
                    <span className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedRequest.status)}`}>
                      {getStatusIcon(selectedRequest.status)}
                      <span className="ml-1">{selectedRequest.status.charAt(0).toUpperCase() + selectedRequest.status.slice(1)}</span>
                    </span>
                  </div>
                  <div><span className="font-medium">Submitted:</span> {format(new Date(selectedRequest.submittedAt), 'MMM d, yyyy • h:mm a')}</div>
                  {selectedRequest.reviewedAt && (
                    <div><span className="font-medium">Reviewed:</span> {format(new Date(selectedRequest.reviewedAt), 'MMM d, yyyy • h:mm a')}</div>
                  )}
                  {selectedRequest.reviewedBy && (
                    <div><span className="font-medium">Reviewed By:</span> {selectedRequest.reviewedBy}</div>
                  )}
                  {selectedRequest.remarks && (
                    <div><span className="font-medium">Remarks:</span> {selectedRequest.remarks}</div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
