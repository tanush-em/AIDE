'use client'

import { useState, useEffect, useRef } from 'react'

export default function ChatInterface() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [useTaskWorkflow, setUseTaskWorkflow] = useState(false)
  const [systemStatus, setSystemStatus] = useState({})
  const [isConnected, setIsConnected] = useState(false)
  const [isReindexing, setIsReindexing] = useState(false)
  const [uploadedDocuments, setUploadedDocuments] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: '1',
        role: 'assistant',
        content: 'Hello! I\'m your AI assistant. How can I help you today?',
        timestamp: new Date(),
        confidence: 'high'
      }
    ])
    checkSystemStatus()
  }, [])

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/health')
      const data = await response.json()
      setSystemStatus(data)
      setIsConnected(true)
    } catch (error) {
      console.error('Error checking system status:', error)
      setIsConnected(false)
    }
  }

  const reindexVectorStore = async () => {
    if (isReindexing) return
    
    setIsReindexing(true)
    try {
      const response = await fetch('http://localhost:5001/api/rag/rebuild', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Add success message to chat
        const successMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `✅ Vector store reindexed successfully! ${data.message || ''} Document count: ${data.document_count || 'Unknown'}`,
          timestamp: new Date(),
          confidence: 'high'
        }
        setMessages(prev => [...prev, successMessage])
      } else {
        // Add error message to chat
        const errorMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `❌ Failed to reindex vector store: ${data.error || data.message || 'Unknown error'}`,
          timestamp: new Date(),
          confidence: 'low'
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Error reindexing vector store:', error)
      const errorMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ Failed to reindex vector store: ${error.message}`,
        timestamp: new Date(),
        confidence: 'low'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsReindexing(false)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const endpoint = useTaskWorkflow 
        ? 'http://localhost:5001/api/tasks/chat'
        : 'http://localhost:5001/api/rag/chat'

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation_history: messages,
          uploaded_documents: uploadedDocuments.map(doc => doc.id)
        }),
      })

      const data = await response.json()
      
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || data.message || 'Sorry, I couldn\'t process your request.',
        timestamp: new Date(),
        confidence: data.confidence || 'medium',
        suggestions: data.suggestions || [],
        agentStatus: data.agent_status || {},
        tasks: data.tasks || [],
        taskExecutionSummary: data.task_execution_summary || null,
        documentSources: data.document_sources || [],
        workflowType: useTaskWorkflow ? 'task_workflow' : 'rag'
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        confidence: 'low'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high': return 'text-green-600 bg-green-100'
      case 'medium': return 'text-yellow-600 bg-yellow-100'
      case 'low': return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files)
    if (files.length === 0) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        setUploadProgress((i / files.length) * 100)

        const formData = new FormData()
        formData.append('file', file)
        formData.append('session_id', 'current_session') // You might want to generate a proper session ID

        const response = await fetch('http://localhost:5001/api/rag/upload', {
          method: 'POST',
          body: formData,
        })

        if (response.ok) {
          const result = await response.json()
          setUploadedDocuments(prev => [...prev, {
            id: result.document_id,
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: new Date(),
            status: 'uploaded'
          }])

          // Add success message to chat
          const successMessage = {
            id: Date.now().toString(),
            role: 'assistant',
            content: `📄 Document "${file.name}" uploaded successfully and is now available for queries!`,
            timestamp: new Date(),
            confidence: 'high'
          }
          setMessages(prev => [...prev, successMessage])
        } else {
          const error = await response.json()
          const errorMessage = {
            id: Date.now().toString(),
            role: 'assistant',
            content: `❌ Failed to upload "${file.name}": ${error.error || 'Unknown error'}`,
            timestamp: new Date(),
            confidence: 'low'
          }
          setMessages(prev => [...prev, errorMessage])
        }
      }
    } catch (error) {
      console.error('Error uploading files:', error)
      const errorMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `❌ Error uploading files: ${error.message}`,
        timestamp: new Date(),
        confidence: 'low'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const removeUploadedDocument = async (documentId) => {
    try {
      const response = await fetch(`http://localhost:5001/api/rag/upload/${documentId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setUploadedDocuments(prev => prev.filter(doc => doc.id !== documentId))
        const successMessage = {
          id: Date.now().toString(),
          role: 'assistant',
          content: `🗑️ Document removed successfully!`,
          timestamp: new Date(),
          confidence: 'high'
        }
        setMessages(prev => [...prev, successMessage])
      }
    } catch (error) {
      console.error('Error removing document:', error)
    }
  }

  const exportConversation = (format) => {
    const data = {
      messages: messages,
      timestamp: new Date().toISOString(),
      format: format
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { 
      type: 'application/json' 
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation_${new Date().toISOString().split('T')[0]}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-200px)]">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">AI Assistant</h2>
            <p className="text-sm text-gray-600">
              {useTaskWorkflow ? 'Task Workflow Mode' : 'RAG Mode'}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {/* System Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            
            {/* Mode Toggle */}
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">RAG</span>
              <button
                onClick={() => setUseTaskWorkflow(!useTaskWorkflow)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  useTaskWorkflow ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    useTaskWorkflow ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
              <span className="text-sm text-gray-600">Tasks</span>
            </div>

            {/* Document Upload Button */}
            <div className="relative">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md,.json,.csv,.xlsx,.xls,.pptx,.ppt"
                onChange={handleFileUpload}
                className="hidden"
                disabled={isUploading}
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
                className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-1"
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-green-600"></div>
                    <span>Uploading...</span>
                  </>
                ) : (
                  <>
                    <span>📄</span>
                    <span>Upload Docs</span>
                  </>
                )}
              </button>
            </div>

            {/* Reindex Button */}
            <button
              onClick={reindexVectorStore}
              disabled={isReindexing}
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-1"
            >
              {isReindexing ? (
                <>
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-blue-600"></div>
                  <span>Reindexing...</span>
                </>
              ) : (
                <>
                  <span>🔄</span>
                  <span>Reindex</span>
                </>
              )}
            </button>

            {/* System Status Button */}
            <button
              onClick={() => checkSystemStatus()}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
            >
              Check Status
            </button>
          </div>
        </div>
      </div>

      {/* Uploaded Documents Panel */}
      {uploadedDocuments.length > 0 && (
        <div className="bg-blue-50 border-b border-blue-200 p-3">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-blue-900">Uploaded Documents ({uploadedDocuments.length})</h3>
            <span className="text-xs text-blue-600">These documents have priority in search results</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {uploadedDocuments.map((doc) => (
              <div key={doc.id} className="flex items-center space-x-2 bg-white rounded-lg px-3 py-2 border border-blue-200 hover:shadow-sm transition-shadow">
                <span className="text-blue-600">📄</span>
                <div className="flex flex-col min-w-0 flex-1">
                  <span className="text-sm text-gray-700 truncate max-w-32" title={doc.name}>
                    {doc.name}
                  </span>
                  <span className="text-xs text-gray-500">
                    {(doc.size / 1024).toFixed(1)} KB
                  </span>
                </div>
                <button
                  onClick={() => removeUploadedDocument(doc.id)}
                  className="text-red-500 hover:text-red-700 text-xs p-1 rounded hover:bg-red-50 transition-colors"
                  title="Remove document"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Progress */}
      {isUploading && (
        <div className="bg-green-50 border-b border-green-200 p-3">
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-green-600"></div>
            <span className="text-sm text-green-700">Uploading documents...</span>
          </div>
          <div className="mt-2 w-full bg-green-200 rounded-full h-2">
            <div 
              className="bg-green-600 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl px-4 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {/* Message Metadata */}
              <div className={`mt-2 text-xs ${
                message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                <div className="flex items-center justify-between">
                  <span>{formatTimestamp(message.timestamp)}</span>
                  {message.confidence && (
                    <span className={`px-2 py-1 rounded-full text-xs ${getConfidenceColor(message.confidence)}`}>
                      {message.confidence} confidence
                    </span>
                  )}
                </div>
                
                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium mb-1">Suggestions:</p>
                    <div className="flex flex-wrap gap-1">
                      {message.suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => setInputMessage(suggestion)}
                          className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200 transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Task Information */}
                {message.tasks && message.tasks.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium mb-1">Tasks Executed:</p>
                    <div className="space-y-1">
                      {message.tasks.map((task, index) => (
                        <div key={index} className="text-xs bg-white bg-opacity-50 p-2 rounded">
                          <div className="font-medium">{task.task_type}</div>
                          <div className="text-gray-600">{task.description}</div>
                          <div className={`inline-block px-2 py-1 rounded text-xs ${
                            task.status === 'completed' ? 'bg-green-100 text-green-800' :
                            task.status === 'failed' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {task.status}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Document Sources */}
                {message.documentSources && message.documentSources.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium mb-1">Sources:</p>
                    <div className="flex flex-wrap gap-1">
                      {message.documentSources.map((source, index) => (
                        <span 
                          key={index}
                          className={`text-xs px-2 py-1 rounded ${
                            source.is_priority 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-600'
                          }`}
                          title={source.is_priority ? 'From uploaded document' : 'From knowledge base'}
                        >
                          {source.is_priority ? '📄' : '📚'} {source.source}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Agent Status */}
                {message.agentStatus && Object.keys(message.agentStatus).length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs font-medium mb-1">Agent Status:</p>
                    <div className="space-y-1">
                      {Object.entries(message.agentStatus).map(([agent, status]) => (
                        <div key={agent} className="text-xs">
                          <span className="font-medium">{agent}:</span> {status}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                <span>Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
        
        {/* Export Options */}
        <div className="mt-2 flex justify-end space-x-2">
          <button
            onClick={() => exportConversation('json')}
            className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
          >
            Export JSON
          </button>
          <button
            onClick={() => exportConversation('txt')}
            className="text-xs text-gray-500 hover:text-gray-700 transition-colors"
          >
            Export TXT
          </button>
        </div>
      </div>
    </div>
  )
}
