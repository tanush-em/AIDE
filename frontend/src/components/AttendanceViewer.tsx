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

interface Student {
  id: string
  name: string
  rollNumber: string
  email: string
  course: string
  attendance: AttendanceRecord[]
}

interface AttendanceRecord {
  date: string
  status: 'present' | 'absent' | 'late' | 'excused'
  class: string
  remarks?: string
}

interface AttendanceStats {
  totalClasses: number
  present: number
  absent: number
  late: number
  excused: number
  attendanceRate: number
}

export default function AttendanceViewer() {
  const [students, setStudents] = useState<Student[]>([])
  const [filteredStudents, setFilteredStudents] = useState<Student[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCourse, setSelectedCourse] = useState('all')
  const [selectedDateRange, setSelectedDateRange] = useState('week')
  const [loading, setLoading] = useState(true)
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)

  const courses = ['all', 'CS101', 'CS201', 'CS301', 'MATH101']

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      const mockStudents: Student[] = [
        {
          id: '1',
          name: 'Alice Johnson',
          rollNumber: 'CS001',
          email: 'alice.johnson@university.edu',
          course: 'CS101',
          attendance: [
            { date: '2024-01-15', status: 'present', class: 'Data Structures' },
            { date: '2024-01-16', status: 'present', class: 'Data Structures' },
            { date: '2024-01-17', status: 'late', class: 'Data Structures' },
            { date: '2024-01-18', status: 'present', class: 'Data Structures' },
            { date: '2024-01-19', status: 'absent', class: 'Data Structures' },
          ]
        },
        {
          id: '2',
          name: 'Bob Smith',
          rollNumber: 'CS002',
          email: 'bob.smith@university.edu',
          course: 'CS101',
          attendance: [
            { date: '2024-01-15', status: 'present', class: 'Data Structures' },
            { date: '2024-01-16', status: 'present', class: 'Data Structures' },
            { date: '2024-01-17', status: 'present', class: 'Data Structures' },
            { date: '2024-01-18', status: 'present', class: 'Data Structures' },
            { date: '2024-01-19', status: 'present', class: 'Data Structures' },
          ]
        },
        {
          id: '3',
          name: 'Carol Davis',
          rollNumber: 'CS003',
          email: 'carol.davis@university.edu',
          course: 'CS201',
          attendance: [
            { date: '2024-01-15', status: 'present', class: 'Algorithms' },
            { date: '2024-01-16', status: 'absent', class: 'Algorithms' },
            { date: '2024-01-17', status: 'present', class: 'Algorithms' },
            { date: '2024-01-18', status: 'excused', class: 'Algorithms' },
            { date: '2024-01-19', status: 'present', class: 'Algorithms' },
          ]
        }
      ]
      setStudents(mockStudents)
      setFilteredStudents(mockStudents)
      setLoading(false)
    }, 1000)
  }, [])

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

  const getAttendanceStats = (student: Student): AttendanceStats => {
    const attendance = student.attendance
    const totalClasses = attendance.length
    const present = attendance.filter(a => a.status === 'present').length
    const absent = attendance.filter(a => a.status === 'absent').length
    const late = attendance.filter(a => a.status === 'late').length
    const excused = attendance.filter(a => a.status === 'excused').length
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'present': return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'absent': return <XCircle className="h-4 w-4 text-red-600" />
      case 'late': return <Clock className="h-4 w-4 text-yellow-600" />
      case 'excused': return <Clock className="h-4 w-4 text-blue-600" />
      default: return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'present': return 'bg-green-100 text-green-800'
      case 'absent': return 'bg-red-100 text-red-800'
      case 'late': return 'bg-yellow-100 text-yellow-800'
      case 'excused': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getAttendanceRateColor = (rate: number) => {
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
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="h-4 w-4" />
            <span>Mark Attendance</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="h-4 w-4" />
            <span>Export</span>
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
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="semester">This Semester</option>
            </select>
          </div>
        </div>
      </div>

      {/* Students List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">
            Students ({filteredStudents.length})
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Student
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Course
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Attendance Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredStudents.map((student) => {
                const stats = getAttendanceStats(student)
                return (
                  <tr key={student.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{student.name}</div>
                        <div className="text-sm text-gray-500">{student.rollNumber}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {student.course}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-1">
                          <div className="flex items-center justify-between text-sm">
                            <span className={`font-medium ${getAttendanceRateColor(stats.attendanceRate)}`}>
                              {stats.attendanceRate.toFixed(1)}%
                            </span>
                            <span className="text-gray-500">
                              {stats.present + stats.late}/{stats.totalClasses}
                            </span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                            <div
                              className={`h-2 rounded-full ${
                                stats.attendanceRate >= 90 ? 'bg-green-500' :
                                stats.attendanceRate >= 75 ? 'bg-yellow-500' : 'bg-red-500'
                              }`}
                              style={{ width: `${Math.min(stats.attendanceRate, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {stats.attendanceRate >= 90 ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          Good
                        </span>
                      ) : stats.attendanceRate >= 75 ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <Clock className="h-3 w-3 mr-1" />
                          Warning
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <TrendingDown className="h-3 w-3 mr-1" />
                          Poor
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => setSelectedStudent(student)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Student Details Modal */}
      {selectedStudent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">
                  {selectedStudent.name} - Attendance Details
                </h3>
                <button
                  onClick={() => setSelectedStudent(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-600">Roll Number</p>
                  <p className="font-medium">{selectedStudent.rollNumber}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Course</p>
                  <p className="font-medium">{selectedStudent.course}</p>
                </div>
              </div>
              
              <h4 className="font-medium text-gray-900 mb-4">Attendance History</h4>
              <div className="space-y-3">
                {selectedStudent.attendance.map((record, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(record.status)}
                      <div>
                        <p className="font-medium text-gray-900">{record.class}</p>
                        <p className="text-sm text-gray-600">{format(new Date(record.date), 'MMM d, yyyy')}</p>
                      </div>
                    </div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(record.status)}`}>
                      {record.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
