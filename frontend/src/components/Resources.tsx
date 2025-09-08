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

interface ResourceFile {
  name: string
  path: string
  size: number
  modified: string
  extension: string
  type: string
  mime_type: string
}

interface ResourceStats {
  total_files: number
  total_size: number
  file_types: Record<string, number>
}

export default function Resources() {
  const [files, setFiles] = useState<ResourceFile[]>([])
  const [stats, setStats] = useState<ResourceStats>({ total_files: 0, total_size: 0, file_types: {} })
  const [loading, setLoading] = useState(true)
  const [selectedFile, setSelectedFile] = useState<ResourceFile | null>(null)
  const [fileContent, setFileContent] = useState<string>('')
  const [parsedContent, setParsedContent] = useState<any>(null)
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
    }
  }

  const handleViewFile = async (file: ResourceFile) => {
    try {
      const response = await fetch(`http://localhost:5001/api/resources/${file.name}/view`)
      const data = await response.json()
      if (data.success) {
        setSelectedFile(file)
        setFileContent(data.data.content)
        setParsedContent(data.data.parsed_content)
        setViewingFile(true)
      }
    } catch (error) {
      console.error('Error viewing file:', error)
    }
  }

  const handleDownloadFile = async (file: ResourceFile) => {
    try {
      const response = await fetch(`http://localhost:5001/api/resources/${file.name}/download`)
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = file.name
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
      }
    } catch (error) {
      console.error('Error downloading file:', error)
    }
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'csv':
      case 'excel':
        return <FileSpreadsheet className="h-5 w-5 text-green-600" />
      case 'json':
        return <FileJson className="h-5 w-5 text-yellow-600" />
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-600" />
      case 'word':
        return <FileType className="h-5 w-5 text-blue-600" />
      case 'image':
        return <FileImage className="h-5 w-5 text-purple-600" />
      case 'text':
      case 'markdown':
        return <FileText className="h-5 w-5 text-gray-600" />
      default:
        return <File className="h-5 w-5 text-gray-500" />
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterType === 'all' || file.type === filterType
    return matchesSearch && matchesFilter
  })

  const renderFileContent = () => {
    if (!selectedFile || !fileContent) return null

    if (selectedFile.type === 'image') {
      return (
        <div className="text-center">
          <img 
            src={fileContent} 
            alt={selectedFile.name}
            className="max-w-full max-h-96 mx-auto rounded-lg shadow-lg"
          />
        </div>
      )
    }

    if (selectedFile.type === 'json' && parsedContent) {
      return (
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900">Parsed JSON Data:</h4>
          <div className="bg-gray-50 p-4 rounded-lg">
            <pre className="text-sm overflow-auto max-h-96">
              {JSON.stringify(parsedContent, null, 2)}
            </pre>
          </div>
        </div>
      )
    }

    if (selectedFile.type === 'csv' && parsedContent) {
      return (
        <div className="space-y-4">
          <h4 className="font-semibold text-gray-900">CSV Data:</h4>
          <div className="overflow-auto max-h-96">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {Object.keys(parsedContent[0] || {}).map((key) => (
                    <th key={key} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {parsedContent.slice(0, 10).map((row: any, index: number) => (
                  <tr key={index}>
                    {Object.values(row).map((value: any, cellIndex: number) => (
                      <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {String(value)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {parsedContent.length > 10 && (
              <p className="text-sm text-gray-500 mt-2">
                Showing first 10 rows of {parsedContent.length} total rows
              </p>
            )}
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900">File Content:</h4>
        <div className="bg-gray-50 p-4 rounded-lg">
          <pre className="text-sm overflow-auto max-h-96 whitespace-pre-wrap">
            {fileContent}
          </pre>
        </div>
      </div>
    )
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
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-100 p-3 rounded-lg">
            <FolderOpen className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Resources</h1>
            <p className="text-gray-600">Access and view all resource files</p>
          </div>
        </div>
      </div>

      {/* Stats */}
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
              <Filter className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex flex-col md:flex-row gap-4">
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
          <div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Types</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="excel">Excel</option>
              <option value="pdf">PDF</option>
              <option value="word">Word</option>
              <option value="text">Text</option>
              <option value="image">Image</option>
            </select>
          </div>
        </div>
      </div>

      {/* Files List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Resource Files</h3>
          <p className="text-sm text-gray-600">Click to view or download files</p>
        </div>
        <div className="divide-y">
          {filteredFiles.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No files found matching your criteria.
            </div>
          ) : (
            filteredFiles.map((file) => (
              <div key={file.name} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      {getFileIcon(file.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center">
                          <Calendar className="h-3 w-3 mr-1" />
                          {formatDate(file.modified)}
                        </span>
                        <span>{formatFileSize(file.size)}</span>
                        <span className="uppercase">{file.type}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleViewFile(file)}
                      className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                      title="View file"
                    >
                      <Eye className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDownloadFile(file)}
                      className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                      title="Download file"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* File Viewer Modal */}
      {viewingFile && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getFileIcon(selectedFile.type)}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{selectedFile.name}</h3>
                  <p className="text-sm text-gray-600">
                    {formatFileSize(selectedFile.size)} • {formatDate(selectedFile.modified)}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleDownloadFile(selectedFile)}
                  className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                  title="Download file"
                >
                  <Download className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setViewingFile(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <span className="text-xl">×</span>
                </button>
              </div>
            </div>
            <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
              {renderFileContent()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
