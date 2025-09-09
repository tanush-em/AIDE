'use client'

import { useState, useEffect } from 'react'
import { 
  Building2, 
  Search, 
  Plus,
  Edit,
  Trash2,
  Eye,
  Calendar,
  MapPin,
  Users,
  DollarSign,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Filter,
  Download,
  ExternalLink,
  Briefcase,
  GraduationCap,
  Target
} from 'lucide-react'
import { format, isAfter, isBefore } from 'date-fns'

export default function Placements() {
  const [drives, setDrives] = useState([])
  const [filteredDrives, setFilteredDrives] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [branchFilter, setBranchFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [selectedDrive, setSelectedDrive] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [editingDrive, setEditingDrive] = useState(null)

  const statusOptions = ['all', 'upcoming', 'ongoing', 'completed', 'cancelled']
  const branchOptions = ['all', 'CSE', 'IT', 'ECE', 'EEE', 'MECH', 'CIVIL', 'CHEM']

  useEffect(() => {
    loadPlacementDrives()
  }, [])

  const loadPlacementDrives = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/placements')
      const data = await response.json()
      if (data.success) {
        setDrives(data.data)
        setFilteredDrives(data.data)
      }
    } catch (error) {
      console.error('Error loading placement drives:', error)
    } finally {
      setLoading(false)
    }
  }

  const updatePlacementDrive = async (driveId, updatedData) => {
    try {
      const response = await fetch(`http://localhost:5001/api/placements/${driveId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData),
      })
      const data = await response.json()
      if (data.success) {
        // Reload drives to get updated data
        await loadPlacementDrives()
        return true
      }
      return false
    } catch (error) {
      console.error('Error updating placement drive:', error)
      return false
    }
  }

  const deletePlacementDrive = async (driveId) => {
    try {
      const response = await fetch(`http://localhost:5001/api/placements/${driveId}`, {
        method: 'DELETE',
      })
      const data = await response.json()
      if (data.success) {
        // Reload drives to get updated data
        await loadPlacementDrives()
        return true
      }
      return false
    } catch (error) {
      console.error('Error deleting placement drive:', error)
      return false
    }
  }

  useEffect(() => {
    let filtered = drives

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(drive =>
        drive.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        drive.jobTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
        drive.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (drive.tags && drive.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase())))
      )
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(drive => drive.status === statusFilter)
    }

    // Filter by branch
    if (branchFilter !== 'all') {
      filtered = filtered.filter(drive => 
        drive.eligibilityCriteria.branches.includes(branchFilter)
      )
    }

    setFilteredDrives(filtered)
  }, [drives, searchTerm, statusFilter, branchFilter])

  const getPlacementStats = () => {
    const totalDrives = drives.length
    const upcomingDrives = drives.filter(d => d.status === 'upcoming').length
    const ongoingDrives = drives.filter(d => d.status === 'ongoing').length
    const completedDrives = drives.filter(d => d.status === 'completed').length
    const totalApplications = drives.reduce((sum, d) => sum + d.totalApplications, 0)
    const totalSelected = drives.reduce((sum, d) => sum + d.selected, 0)
    const averageSalary = drives.length > 0 
      ? drives.reduce((sum, d) => sum + (d.salaryRange.min + d.salaryRange.max) / 2, 0) / drives.length
      : 0

    return {
      totalDrives,
      upcomingDrives,
      ongoingDrives,
      completedDrives,
      totalApplications,
      totalSelected,
      averageSalary
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'upcoming': return 'bg-blue-100 text-blue-800'
      case 'ongoing': return 'bg-green-100 text-green-800'
      case 'completed': return 'bg-gray-100 text-gray-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'upcoming': return <Clock className="h-4 w-4" />
      case 'ongoing': return <CheckCircle className="h-4 w-4" />
      case 'completed': return <CheckCircle className="h-4 w-4" />
      case 'cancelled': return <XCircle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const formatSalary = (salaryRange) => {
    return `${salaryRange.currency} ${(salaryRange.min / 100000).toFixed(1)}L - ${(salaryRange.max / 100000).toFixed(1)}L`
  }

  const isRegistrationOpen = (drive) => {
    return isBefore(new Date(), new Date(drive.registrationDeadline))
  }

  const stats = getPlacementStats()

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
          <h2 className="text-2xl font-bold text-gray-900">Placement Drives</h2>
          <p className="text-gray-600">Manage and track placement opportunities for students</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={() => {
              // Export functionality - could export to CSV or PDF
              alert('Export functionality will be implemented soon')
            }}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button 
            onClick={() => {
              alert('Add Drive functionality will be implemented soon')
            }}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>Add Drive</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Drives</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalDrives}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Briefcase className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Upcoming Drives</p>
              <p className="text-2xl font-bold text-blue-600">{stats.upcomingDrives}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Ongoing Drives</p>
              <p className="text-2xl font-bold text-green-600">{stats.ongoingDrives}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Selected</p>
              <p className="text-2xl font-bold text-purple-600">{stats.totalSelected}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <Target className="h-6 w-6 text-purple-600" />
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
                placeholder="Search companies, job titles, locations..."
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
              value={branchFilter}
              onChange={(e) => setBranchFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {branchOptions.map(branch => (
                <option key={branch} value={branch}>
                  {branch === 'all' ? 'All Branches' : branch}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Drives List */}
      <div className="space-y-4">
        {filteredDrives.map((drive) => (
          <div key={drive.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <Building2 className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{drive.companyName}</h3>
                      <p className="text-gray-600">{drive.jobTitle}</p>
                    </div>
                  </div>
                  
                  <p className="text-gray-700 mb-4 line-clamp-2">{drive.jobDescription}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <MapPin className="h-4 w-4" />
                      <span>{drive.location}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <DollarSign className="h-4 w-4" />
                      <span>{formatSalary(drive.salaryRange)}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>{format(new Date(drive.driveDate), 'MMM d, yyyy')}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4 mb-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(drive.status)}`}>
                      {getStatusIcon(drive.status)}
                      <span className="ml-1">{drive.status.charAt(0).toUpperCase() + drive.status.slice(1)}</span>
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                      Min CGPA: {drive.eligibilityCriteria.minCGPA}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {drive.eligibilityCriteria.branches.join(', ')}
                    </span>
                    {isRegistrationOpen(drive) ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Registration Open
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Registration Closed
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Applications: {drive.totalApplications} | Shortlisted: {drive.shortlisted} | Selected: {drive.selected}</span>
                    <span>
                      Deadline: {format(new Date(drive.registrationDeadline), 'MMM d, yyyy')}
                    </span>
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2 ml-4">
                  <button
                    onClick={() => setSelectedDrive(drive)}
                    className="flex items-center space-x-1 px-3 py-1 text-blue-600 hover:text-blue-800 text-sm"
                  >
                    <Eye className="h-4 w-4" />
                    <span>View</span>
                  </button>
                  <button
                    onClick={() => {
                      alert('Edit functionality will be implemented soon')
                    }}
                    className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800 text-sm"
                  >
                    <Edit className="h-4 w-4" />
                    <span>Edit</span>
                  </button>
                  <button 
                    onClick={async () => {
                      if (window.confirm('Are you sure you want to delete this placement drive?')) {
                        const success = await deletePlacementDrive(drive.id)
                        if (success) {
                          alert('Placement drive deleted successfully')
                        } else {
                          alert('Failed to delete placement drive')
                        }
                      }
                    }}
                    className="flex items-center space-x-1 px-3 py-1 text-red-600 hover:text-red-800 text-sm"
                  >
                    <Trash2 className="h-4 w-4" />
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Drive Details Modal */}
      {selectedDrive && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedDrive.companyName}</h3>
                  <p className="text-lg text-gray-600">{selectedDrive.jobTitle}</p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                    <span className="flex items-center space-x-1">
                      <MapPin className="h-4 w-4" />
                      <span>{selectedDrive.location}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <DollarSign className="h-4 w-4" />
                      <span>{formatSalary(selectedDrive.salaryRange)}</span>
                    </span>
                    <span className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>{format(new Date(selectedDrive.driveDate), 'MMM d, yyyy')}</span>
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedDrive(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-6">
              {/* Job Description */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Job Description</h4>
                <p className="text-gray-700">{selectedDrive.jobDescription}</p>
              </div>

              {/* Requirements */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Requirements</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-700">
                  {selectedDrive.requirements.map((req, index) => (
                    <li key={index}>{req}</li>
                  ))}
                </ul>
              </div>

              {/* Eligibility Criteria */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Eligibility Criteria</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Minimum CGPA:</span> {selectedDrive.eligibilityCriteria.minCGPA}
                  </div>
                  <div>
                    <span className="font-medium">Eligible Branches:</span> {selectedDrive.eligibilityCriteria.branches.join(', ')}
                  </div>
                  <div>
                    <span className="font-medium">Year of Passing:</span> {selectedDrive.eligibilityCriteria.yearOfPassing.join(', ')}
                  </div>
                  <div>
                    <span className="font-medium">Max Backlogs:</span> {selectedDrive.eligibilityCriteria.backlogs}
                  </div>
                </div>
              </div>

              {/* Selection Process */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Selection Process</h4>
                <div className="space-y-2">
                  <div>
                    <span className="font-medium">Rounds:</span>
                    <ul className="list-disc list-inside ml-4 mt-1">
                      {selectedDrive.process.rounds.map((round, index) => (
                        <li key={index} className="text-gray-700">{round}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <span className="font-medium">Duration:</span> {selectedDrive.process.duration}
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Contact Information</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="font-medium">Name:</span> {selectedDrive.contactPerson.name}</div>
                  <div><span className="font-medium">Email:</span> {selectedDrive.contactPerson.email}</div>
                  <div><span className="font-medium">Phone:</span> {selectedDrive.contactPerson.phone}</div>
                </div>
              </div>

              {/* Statistics */}
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Drive Statistics</h4>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-blue-50 p-3 rounded">
                    <div className="text-2xl font-bold text-blue-600">{selectedDrive.totalApplications}</div>
                    <div className="text-sm text-gray-600">Applications</div>
                  </div>
                  <div className="bg-yellow-50 p-3 rounded">
                    <div className="text-2xl font-bold text-yellow-600">{selectedDrive.shortlisted}</div>
                    <div className="text-sm text-gray-600">Shortlisted</div>
                  </div>
                  <div className="bg-green-50 p-3 rounded">
                    <div className="text-2xl font-bold text-green-600">{selectedDrive.selected}</div>
                    <div className="text-sm text-gray-600">Selected</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
