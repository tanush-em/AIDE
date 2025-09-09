'use client'

import { useState, useEffect } from 'react'
import { 
  Search, 
  Download, 
  Plus,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  TrendingDown
} from 'lucide-react'
import { format } from 'date-fns'

export default function AttendanceViewer() {
  const [students, setStudents] = useState([])
  const [filteredStudents, setFilteredStudents] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCourse, setSelectedCourse] = useState('all')
  const [selectedDateRange, setSelectedDateRange] = useState('week')
  const [loading, setLoading] = useState(true)
  const [selectedStudent, setSelectedStudent] = useState(null)

  const courses = ['all', 'CS101', 'CS201', 'CS301', 'MATH101']
  const dateRanges = [
    { value: 'week', label: 'This Week' },
    { value: 'month', label: 'This Month' },
    { value: 'semester', label: 'This Semester' }
  ]

  useEffect(() => {
    loadStudents()
  }, [])

  const loadStudents = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/attendance/students')
      const data = await response.json()
      if (data.success) {
        setStudents(data.data)
        setFilteredStudents(data.data)
      }
    } catch (error) {
      console.error('Error loading students:', error)
      // Fallback to mock data
      const mockStudents = [
        {
          id: '1',
          name: 'John Smith',
          rollNumber: 'CS2024001',
          email: 'john.smith@student.edu',
          course: 'CS101',
          attendance: [
            { date: '2024-01-15', status: 'present', class: 'CS101', remarks: '' },
            { date: '2024-01-16', status: 'present', class: 'CS101', remarks: '' },
            { date: '2024-01-17', status: 'late', class: 'CS101', remarks: 'Traffic delay' },
            { date: '2024-01-18', status: 'absent', class: 'CS101', remarks: 'Sick' },
            { date: '2024-01-19', status: 'present', class: 'CS101', remarks: '' }
          ]
        },
        {
          id: '2',
          name: 'Sarah Johnson',
          rollNumber: 'CS2024002',
          email: 'sarah.johnson@student.edu',
          course: 'CS101',
          attendance: [
            { date: '2024-01-15', status: 'present', class: 'CS101', remarks: '' },
            { date: '2024-01-16', status: 'present', class: 'CS101', remarks: '' },
            { date: '2024-01-17', status: 'present', class: 'CS101', remarks: '' },
            { date: '2024-01-18', status: 'present', class: 'CS101', remarks: '' },
            { date: '2024-01-19', status: 'excused', class: 'CS101', remarks: 'Medical appointment' }
          ]
        },
        {
          id: '3',
          name: 'Michael Chen',
          rollNumber: 'CS2024003',
          email: 'michael.chen@student.edu',
          course: 'CS201',
          attendance: [
            { date: '2024-01-15', status: 'present', class: 'CS201', remarks: '' },
            { date: '2024-01-16', status: 'absent', class: 'CS201', remarks: 'Family emergency' },
            { date: '2024-01-17', status: 'present', class: 'CS201', remarks: '' },
            { date: '2024-01-18', status: 'present', class: 'CS201', remarks: '' },
            { date: '2024-01-19', status: 'present', class: 'CS201', remarks: '' }
          ]
        }
      ]
      setStudents(mockStudents)
      setFilteredStudents(mockStudents)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let filtered = students

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(student =>
        student.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.rollNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.email.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    // Filter by course
    if (selectedCourse !== 'all') {
      filtered = filtered.filter(student => student.course === selectedCourse)
    }

    setFilteredStudents(filtered)
  }, [students, searchTerm, selectedCourse])

  const getAttendanceStats = (student) => {
    const totalClasses = student.attendance.length
    const present = student.attendance.filter(a => a.status === 'present').length
    const absent = student.attendance.filter(a => a.status === 'absent').length
    const late = student.attendance.filter(a => a.status === 'late').length
    const excused = student.attendance.filter(a => a.status === 'excused').length
    const attendanceRate = totalClasses > 0 ? ((present + late) / totalClasses) * 100 : 0

    return {
      totalClasses,
      present,
      absent,
      late,
      excused,
      attendanceRate
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'present': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'absent': return <XCircle className="h-4 w-4 text-red-600" />
      case 'late': return <Clock className="h-4 w-4 text-yellow-600" />
      case 'excused': return <Clock className="h-4 w-4 text-blue-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'present': return 'bg-green-100 text-green-800'
      case 'absent': return 'bg-red-100 text-red-800'
      case 'late': return 'bg-yellow-100 text-yellow-800'
      case 'excused': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getAttendanceRateColor = (rate) => {
    if (rate >= 90) return 'text-green-600'
    if (rate >= 75) return 'text-yellow-600'
    return 'text-red-600'
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
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Attendance Management</h2>
          <p className="text-gray-600">Track and manage student attendance</p>
        </div>
        <div className="flex space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="h-4 w-4" />
            <span>Mark Attendance</span>
          </button>
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
              value={selectedCourse}
              onChange={(e) => setSelectedCourse(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {courses.map(course => (
                <option key={course} value={course}>
                  {course === 'all' ? 'All Courses' : course}
                </option>
              ))}
            </select>
            <select
              value={selectedDateRange}
              onChange={(e) => setSelectedDateRange(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {dateRanges.map(range => (
                <option key={range.value} value={range.value}>
                  {range.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Students List */}
      <div className="space-y-4">
        {filteredStudents.map((student) => {
          const stats = getAttendanceStats(student)
          return (
            <div key={student.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-4">
                    <div className="bg-blue-100 p-3 rounded-full">
                      <span className="text-lg font-semibold text-blue-600">
                        {student.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{student.name}</h3>
                      <p className="text-sm text-gray-600">{student.rollNumber} • {student.course}</p>
                      <p className="text-sm text-gray-500">{student.email}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-2xl font-bold ${getAttendanceRateColor(stats.attendanceRate)}`}>
                      {stats.attendanceRate.toFixed(1)}%
                    </div>
                    <p className="text-sm text-gray-600">Attendance Rate</p>
                  </div>
                </div>

                {/* Attendance Stats */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">{stats.totalClasses}</div>
                    <div className="text-sm text-gray-600">Total Classes</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-600">{stats.present}</div>
                    <div className="text-sm text-gray-600">Present</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-red-600">{stats.absent}</div>
                    <div className="text-sm text-gray-600">Absent</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-yellow-600">{stats.late}</div>
                    <div className="text-sm text-gray-600">Late</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-blue-600">{stats.excused}</div>
                    <div className="text-sm text-gray-600">Excused</div>
                  </div>
                </div>

                {/* Recent Attendance */}
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-3">Recent Attendance</h4>
                  <div className="space-y-2">
                    {student.attendance.slice(-5).map((record, index) => (
                      <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(record.status)}
                          <span className="text-sm font-medium text-gray-900">
                            {format(new Date(record.date), 'MMM d, yyyy')}
                          </span>
                          <span className="text-sm text-gray-600">{record.class}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(record.status)}`}>
                            {record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                          </span>
                          {record.remarks && (
                            <span className="text-xs text-gray-500" title={record.remarks}>
                              {record.remarks}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end mt-4">
                  <button
                    onClick={() => setSelectedStudent(student)}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Student Details Modal */}
      {selectedStudent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedStudent.name}</h3>
                  <p className="text-gray-600">{selectedStudent.rollNumber} • {selectedStudent.course}</p>
                </div>
                <button
                  onClick={() => setSelectedStudent(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Student Info */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Student Information</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Name:</span> {selectedStudent.name}</div>
                    <div><span className="font-medium">Roll Number:</span> {selectedStudent.rollNumber}</div>
                    <div><span className="font-medium">Email:</span> {selectedStudent.email}</div>
                    <div><span className="font-medium">Course:</span> {selectedStudent.course}</div>
                  </div>
                </div>

                {/* Attendance Summary */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Attendance Summary</h4>
                  {(() => {
                    const stats = getAttendanceStats(selectedStudent)
                    return (
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Total Classes:</span>
                          <span className="font-medium">{stats.totalClasses}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Present:</span>
                          <span className="font-medium text-green-600">{stats.present}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Absent:</span>
                          <span className="font-medium text-red-600">{stats.absent}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Late:</span>
                          <span className="font-medium text-yellow-600">{stats.late}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Excused:</span>
                          <span className="font-medium text-blue-600">{stats.excused}</span>
                        </div>
                        <div className="flex justify-between border-t pt-2">
                          <span>Attendance Rate:</span>
                          <span className={`font-medium ${getAttendanceRateColor(stats.attendanceRate)}`}>
                            {stats.attendanceRate.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    )
                  })()}
                </div>
              </div>

              {/* Full Attendance History */}
              <div className="mt-6">
                <h4 className="font-medium text-gray-900 mb-3">Full Attendance History</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {selectedStudent.attendance.map((record, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(record.status)}
                        <span className="text-sm font-medium text-gray-900">
                          {format(new Date(record.date), 'MMM d, yyyy')}
                        </span>
                        <span className="text-sm text-gray-600">{record.class}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(record.status)}`}>
                          {record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                        </span>
                        {record.remarks && (
                          <span className="text-xs text-gray-500" title={record.remarks}>
                            {record.remarks}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
