'use client'

import { useState, useEffect } from 'react'
import { 
  FolderOpen, 
  FileText, 
  Download, 
  Eye, 
  File, 
  FileSpreadsheet, 
  FileJson, 
  FileImage,
  FileType,
  Calendar,
  HardDrive,
  Filter,
  Search
} from 'lucide-react'

export default function Resources() {
  const [files, setFiles] = useState([])
  const [stats, setStats] = useState({ total_files: 0, total_size: 0, file_types: {} })
  const [loading, setLoading] = useState(true)
  const [selectedFile, setSelectedFile] = useState(null)
  const [fileContent, setFileContent] = useState('')
  const [parsedContent, setParsedContent] = useState(null)
  const [viewingFile, setViewingFile] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')

  useEffect(() => {
    loadResources()
    loadStats()
  }, [])

  const loadResources = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/resources')
      const data = await response.json()
      if (data.success) {
        setFiles(data.data)
      }
    } catch (error) {
      console.error('Error loading resources:', error)
      // Fallback to mock data
      const mockFiles = [
        {
          name: 'course_syllabus.pdf',
          path: '/resources/course_syllabus.pdf',
          size: 2048576,
          modified: '2024-01-15T10:30:00Z',
          extension: 'pdf',
          type: 'document',
          mime_type: 'application/pdf'
        },
        {
          name: 'student_data.csv',
          path: '/resources/student_data.csv',
          size: 512000,
          modified: '2024-01-18T14:20:00Z',
          extension: 'csv',
          type: 'data',
          mime_type: 'text/csv'
        },
        {
          name: 'exam_schedule.json',
          path: '/resources/exam_schedule.json',
          size: 25600,
          modified: '2024-01-20T09:15:00Z',
          extension: 'json',
          type: 'data',
          mime_type: 'application/json'
        },
        {
          name: 'lecture_notes.docx',
          path: '/resources/lecture_notes.docx',
          size: 1536000,
          modified: '2024-01-12T16:45:00Z',
          extension: 'docx',
          type: 'document',
          mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        },
        {
          name: 'assignment_template.xlsx',
          path: '/resources/assignment_template.xlsx',
          size: 76800,
          modified: '2024-01-16T11:30:00Z',
          extension: 'xlsx',
          type: 'spreadsheet',
          mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
      ]
      setFiles(mockFiles)
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/resources/stats')
      const data = await response.json()
      if (data.success) {
        setStats(data.data)
      }
    } catch (error) {
      console.error('Error loading stats:', error)
      // Fallback to mock stats
      setStats({
        total_files: 5,
        total_size: 4563072,
        file_types: {
          'pdf': 1,
          'csv': 1,
          'json': 1,
          'docx': 1,
          'xlsx': 1
        }
      })
    }
  }

  const handleViewFile = async (file) => {
    setSelectedFile(file)
    setViewingFile(true)
    
    try {
      const response = await fetch(`http://localhost:5001/api/resources/view?file=${encodeURIComponent(file.path)}`)
      const data = await response.json()
      
      if (data.success) {
        setFileContent(data.content)
        
        // Try to parse JSON files
        if (file.extension === 'json') {
          try {
            setParsedContent(JSON.parse(data.content))
          } catch (e) {
            setParsedContent(null)
          }
        } else {
          setParsedContent(null)
        }
      } else {
        setFileContent('Unable to load file content')
        setParsedContent(null)
      }
    } catch (error) {
      console.error('Error loading file content:', error)
      setFileContent('Error loading file content')
      setParsedContent(null)
    }
  }

  const handleDownloadFile = async (file) => {
    try {
      const response = await fetch(`http://localhost:5001/api/resources/download?file=${encodeURIComponent(file.path)}`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = file.name
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } else {
        alert('Failed to download file')
      }
    } catch (error) {
      console.error('Error downloading file:', error)
      alert('Error downloading file')
    }
  }

  const getFileIcon = (extension) => {
    switch (extension) {
      case 'pdf': return <FileText className="h-5 w-5 text-red-600" />
      case 'docx': return <FileText className="h-5 w-5 text-blue-600" />
      case 'xlsx': return <FileSpreadsheet className="h-5 w-5 text-green-600" />
      case 'csv': return <FileSpreadsheet className="h-5 w-5 text-orange-600" />
      case 'json': return <FileJson className="h-5 w-5 text-yellow-600" />
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif': return <FileImage className="h-5 w-5 text-purple-600" />
      default: return <File className="h-5 w-5 text-gray-600" />
    }
  }

  const getFileTypeColor = (type) => {
    switch (type) {
      case 'document': return 'bg-blue-100 text-blue-800'
      case 'spreadsheet': return 'bg-green-100 text-green-800'
      case 'data': return 'bg-orange-100 text-orange-800'
      case 'image': return 'bg-purple-100 text-purple-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.extension.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || file.type === filterType
    return matchesSearch && matchesType
  })

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
          <h2 className="text-2xl font-bold text-gray-900">Resource Management</h2>
          <p className="text-gray-600">Manage and organize academic resources and files</p>
        </div>
        <div className="flex space-x-3">
          <button className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
            <Download className="h-4 w-4" />
            <span>Bulk Download</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <FolderOpen className="h-4 w-4" />
            <span>Upload Files</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Files</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_files}</p>
            </div>
            <div className="bg-blue-100 p-3 rounded-full">
              <File className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Size</p>
              <p className="text-2xl font-bold text-gray-900">{formatFileSize(stats.total_size)}</p>
            </div>
            <div className="bg-green-100 p-3 rounded-full">
              <HardDrive className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">File Types</p>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(stats.file_types).length}</p>
            </div>
            <div className="bg-purple-100 p-3 rounded-full">
              <FileType className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* File Type Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">File Types</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(stats.file_types).map(([type, count]) => (
            <div key={type} className="text-center">
              <div className="text-2xl font-bold text-gray-900">{count}</div>
              <div className="text-sm text-gray-600 uppercase">{type}</div>
            </div>
          ))}
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
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="flex space-x-3">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="document">Documents</option>
              <option value="spreadsheet">Spreadsheets</option>
              <option value="data">Data Files</option>
              <option value="image">Images</option>
            </select>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Files ({filteredFiles.length})</h3>
          <div className="space-y-3">
            {filteredFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-4">
                  {getFileIcon(file.extension)}
                  <div>
                    <h4 className="font-medium text-gray-900">{file.name}</h4>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <span>{formatFileSize(file.size)}</span>
                      <span>•</span>
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getFileTypeColor(file.type)}`}>
                        {file.type}
                      </span>
                      <span>•</span>
                      <span className="flex items-center space-x-1">
                        <Calendar className="h-3 w-3" />
                        <span>{formatDate(file.modified)}</span>
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleViewFile(file)}
                    className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
                    title="View file"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDownloadFile(file)}
                    className="p-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors"
                    title="Download file"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* File Viewer Modal */}
      {viewingFile && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedFile.name}</h3>
                  <p className="text-gray-600">{formatFileSize(selectedFile.size)} • {selectedFile.type}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleDownloadFile(selectedFile)}
                    className="p-2 text-green-600 hover:text-green-800 hover:bg-green-50 rounded-lg transition-colors"
                    title="Download file"
                  >
                    <Download className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => setViewingFile(false)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <Eye className="h-6 w-6" />
                  </button>
                </div>
              </div>
            </div>
            <div className="p-6">
              {parsedContent ? (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Parsed JSON Content</h4>
                  <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                    {JSON.stringify(parsedContent, null, 2)}
                  </pre>
                </div>
              ) : (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">File Content</h4>
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <pre className="whitespace-pre-wrap text-sm overflow-x-auto">
                      {fileContent}
                    </pre>
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
