'use client'

import { useState, useEffect } from 'react'
import { 
  FileText, 
  Download, 
  Plus,
  Edit,
  Trash2,
  Eye,
  Calendar,
  BookOpen,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Filter,
  Search
} from 'lucide-react'
import { format } from 'date-fns'

export default function QuestionPaper() {
  const [questionPapers, setQuestionPapers] = useState([])
  const [filteredPapers, setFilteredPapers] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [courseFilter, setCourseFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [selectedPaper, setSelectedPaper] = useState(null)

  const courses = ['all', 'CS101', 'CS201', 'CS301', 'MATH101', 'PHYS101']
  const paperTypes = ['all', 'midterm', 'final', 'quiz', 'assignment']

  useEffect(() => {
    loadQuestionPapers()
  }, [])

  const loadQuestionPapers = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/question-paper')
      const data = await response.json()
      if (data.success) {
        setQuestionPapers(data.data)
        setFilteredPapers(data.data)
      }
    } catch (error) {
      console.error('Error loading question papers:', error)
      // Fallback to mock data
      const mockPapers = [
        {
          id: '1',
          title: 'CS101 - Data Structures Midterm Exam',
          course: 'CS101',
          type: 'midterm',
          semester: 'Fall 2024',
          duration: 120,
          totalMarks: 100,
          questions: 5,
          difficulty: 'medium',
          topics: ['Arrays', 'Linked Lists', 'Stacks', 'Queues'],
          createdAt: '2024-01-15T09:00:00Z',
          updatedAt: '2024-01-15T09:00:00Z',
          status: 'published',
          author: 'Dr. Sarah Johnson'
        },
        {
          id: '2',
          title: 'CS201 - Algorithms Final Exam',
          course: 'CS201',
          type: 'final',
          semester: 'Fall 2024',
          duration: 180,
          totalMarks: 150,
          questions: 8,
          difficulty: 'hard',
          topics: ['Sorting', 'Searching', 'Graph Algorithms', 'Dynamic Programming'],
          createdAt: '2024-01-10T14:30:00Z',
          updatedAt: '2024-01-12T10:15:00Z',
          status: 'draft',
          author: 'Dr. Michael Chen'
        },
        {
          id: '3',
          title: 'MATH101 - Calculus Quiz 3',
          course: 'MATH101',
          type: 'quiz',
          semester: 'Fall 2024',
          duration: 45,
          totalMarks: 50,
          questions: 10,
          difficulty: 'easy',
          topics: ['Derivatives', 'Limits', 'Continuity'],
          createdAt: '2024-01-18T11:00:00Z',
          updatedAt: '2024-01-18T11:00:00Z',
          status: 'published',
          author: 'Dr. Emily Davis'
        }
      ]
      setQuestionPapers(mockPapers)
      setFilteredPapers(mockPapers)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let filtered = questionPapers

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(paper =>
        paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        paper.course.toLowerCase().includes(searchTerm.toLowerCase()) ||
        paper.topics.some(topic => topic.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    // Filter by course
    if (courseFilter !== 'all') {
      filtered = filtered.filter(paper => paper.course === courseFilter)
    }

    // Filter by type
    if (typeFilter !== 'all') {
      filtered = filtered.filter(paper => paper.type === typeFilter)
    }

    setFilteredPapers(filtered)
  }, [questionPapers, searchTerm, courseFilter, typeFilter])

  const getPaperStats = () => {
    const totalPapers = questionPapers.length
    const publishedPapers = questionPapers.filter(p => p.status === 'published').length
    const draftPapers = questionPapers.filter(p => p.status === 'draft').length
    const totalQuestions = questionPapers.reduce((sum, p) => sum + p.questions, 0)

    return {
      totalPapers,
      publishedPapers,
      draftPapers,
      totalQuestions
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'bg-green-100 text-green-800'
      case 'draft': return 'bg-yellow-100 text-yellow-800'
      case 'archived': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'published': return <CheckCircle className="h-4 w-4" />
      case 'draft': return <Clock className="h-4 w-4" />
      case 'archived': return <XCircle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'midterm': return 'bg-blue-100 text-blue-800'
      case 'final': return 'bg-purple-100 text-purple-800'
      case 'quiz': return 'bg-orange-100 text-orange-800'
      case 'assignment': return 'bg-indigo-100 text-indigo-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const stats = getPaperStats()

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
          <h2 className="text-2xl font-bold text-gray-900">Question Papers</h2>
          <p className="text-gray-600">Create and manage examination question papers</p>
        </div>
        <div className="flex space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Download className="h-4 w-4" />
            <span>Export</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="h-4 w-4" />
            <span>Create Paper</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Papers</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalPapers}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Published</p>
              <p className="text-2xl font-bold text-green-600">{stats.publishedPapers}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Drafts</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.draftPapers}</p>
            </div>
            <div className="bg-yellow-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Questions</p>
              <p className="text-2xl font-bold text-purple-600">{stats.totalQuestions}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <BookOpen className="h-6 w-6 text-purple-600" />
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
                placeholder="Search papers, courses, topics..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex space-x-3">
            <select
              value={courseFilter}
              onChange={(e) => setCourseFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {courses.map(course => (
                <option key={course} value={course}>
                  {course === 'all' ? 'All Courses' : course}
                </option>
              ))}
            </select>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {paperTypes.map(type => (
                <option key={type} value={type}>
                  {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Papers List */}
      <div className="space-y-4">
        {filteredPapers.map((paper) => (
          <div key={paper.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <FileText className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{paper.title}</h3>
                      <p className="text-sm text-gray-600">{paper.course} • {paper.semester}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Duration</p>
                      <p className="text-sm text-gray-900">{paper.duration} minutes</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Marks</p>
                      <p className="text-sm text-gray-900">{paper.totalMarks}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Questions</p>
                      <p className="text-sm text-gray-900">{paper.questions}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Author</p>
                      <p className="text-sm text-gray-900">{paper.author}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4 mb-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(paper.status)}`}>
                      {getStatusIcon(paper.status)}
                      <span className="ml-1">{paper.status.charAt(0).toUpperCase() + paper.status.slice(1)}</span>
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(paper.type)}`}>
                      {paper.type.charAt(0).toUpperCase() + paper.type.slice(1)}
                    </span>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(paper.difficulty)}`}>
                      {paper.difficulty.charAt(0).toUpperCase() + paper.difficulty.slice(1)}
                    </span>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-sm font-medium text-gray-600 mb-2">Topics Covered</p>
                    <div className="flex flex-wrap gap-1">
                      {paper.topics.map((topic, index) => (
                        <span key={index} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>Created: {format(new Date(paper.createdAt), 'MMM d, yyyy')}</span>
                    {paper.updatedAt !== paper.createdAt && (
                      <span>Updated: {format(new Date(paper.updatedAt), 'MMM d, yyyy')}</span>
                    )}
                  </div>
                </div>
                
                <div className="flex flex-col space-y-2 ml-4">
                  <button
                    onClick={() => setSelectedPaper(paper)}
                    className="flex items-center space-x-1 px-3 py-1 text-blue-600 hover:text-blue-800 text-sm"
                  >
                    <Eye className="h-4 w-4" />
                    <span>View</span>
                  </button>
                  <button className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800 text-sm">
                    <Edit className="h-4 w-4" />
                    <span>Edit</span>
                  </button>
                  <button className="flex items-center space-x-1 px-3 py-1 text-green-600 hover:text-green-800 text-sm">
                    <Download className="h-4 w-4" />
                    <span>Download</span>
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

      {/* Paper Details Modal */}
      {selectedPaper && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedPaper.title}</h3>
                  <p className="text-gray-600">{selectedPaper.course} • {selectedPaper.semester}</p>
                </div>
                <button
                  onClick={() => setSelectedPaper(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="h-6 w-6" />
                </button>
              </div>
            </div>
            <div className="p-6 space-y-6">
              {/* Paper Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Paper Details</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Type:</span> {selectedPaper.type}</div>
                    <div><span className="font-medium">Duration:</span> {selectedPaper.duration} minutes</div>
                    <div><span className="font-medium">Total Marks:</span> {selectedPaper.totalMarks}</div>
                    <div><span className="font-medium">Questions:</span> {selectedPaper.questions}</div>
                    <div><span className="font-medium">Difficulty:</span> {selectedPaper.difficulty}</div>
                    <div><span className="font-medium">Author:</span> {selectedPaper.author}</div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Status Information</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Status:</span> 
                      <span className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedPaper.status)}`}>
                        {getStatusIcon(selectedPaper.status)}
                        <span className="ml-1">{selectedPaper.status.charAt(0).toUpperCase() + selectedPaper.status.slice(1)}</span>
                      </span>
                    </div>
                    <div><span className="font-medium">Created:</span> {format(new Date(selectedPaper.createdAt), 'MMM d, yyyy • h:mm a')}</div>
                    <div><span className="font-medium">Updated:</span> {format(new Date(selectedPaper.updatedAt), 'MMM d, yyyy • h:mm a')}</div>
                  </div>
                </div>
              </div>

              {/* Topics Covered */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Topics Covered</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedPaper.topics.map((topic, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                      {topic}
                    </span>
                  ))}
                </div>
              </div>

              {/* Sample Questions (Mock) */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Sample Questions</h4>
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Q1.</span> Explain the concept of data structures and their importance in computer science. (20 marks)
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Q2.</span> Compare and contrast arrays and linked lists. Provide examples of when to use each. (25 marks)
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">
                      <span className="font-medium">Q3.</span> Implement a stack using arrays and explain the operations. (30 marks)
                    </p>
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
