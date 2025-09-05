'use client'

import { useState, useEffect, useRef } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  confidence?: string
  suggestions?: string[]
  agentStatus?: Record<string, string>
}

interface AgentStatus {
  [key: string]: string
}

const BACKEND_URL = 'http://localhost:5001'

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({})
  const [systemStatus, setSystemStatus] = useState<string>('initializing')
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize session
  useEffect(() => {
    if (!sessionId) {
      setSessionId(crypto.randomUUID())
    }
  }, [sessionId])

  // Check system status
  useEffect(() => {
    checkSystemStatus()
    // Set up periodic status check
    const interval = setInterval(checkSystemStatus, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const checkSystemStatus = async () => {
    try {
      setConnectionError(null)
      
      // Try RAG health first
      let response = await fetch(`${BACKEND_URL}/api/rag/health`)
      if (response.ok) {
        const data = await response.json()
        setSystemStatus(data.status)
        return
      }
      
      // Fallback to main health endpoint
      response = await fetch(`${BACKEND_URL}/api/health`)
      if (response.ok) {
        await response.json() // Just consume the response
        setSystemStatus('healthy')
        return
      }
      
      // If both fail, check if backend is reachable
      response = await fetch(`${BACKEND_URL}/`)
      if (response.ok) {
        setSystemStatus('partial')
        return
      }
      
      setSystemStatus('error')
      setConnectionError('Backend server is not responding')
    } catch (error) {
      setSystemStatus('error')
      setConnectionError('Cannot connect to backend server')
      console.error('Error checking system status:', error)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setAgentStatus({})

    try {
      // Use the RAG chat endpoint
      const response = await fetch(`${BACKEND_URL}/api/rag/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId,
          user_id: 'default'
        }),
      })

      const data = await response.json()

      if (response.ok) {
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          confidence: data.confidence,
          suggestions: data.suggestions,
          agentStatus: data.agent_status
        }

        setMessages(prev => [...prev, assistantMessage])
        setAgentStatus(data.agent_status || {})
      } else {
        const errorMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `Error: ${data.error || 'Failed to get response'}`,
          timestamp: new Date(),
          confidence: 'low'
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Network error:', error)
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Network error: Unable to connect to the backend. Please check if the server is running on port 5001.',
        timestamp: new Date(),
        confidence: 'low'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const exportConversation = async (format: 'json' | 'txt') => {
    if (!sessionId) return

    try {
      const response = await fetch(`${BACKEND_URL}/api/rag/export/${sessionId}?format=${format}`)
      const data = await response.json()

      if (response.ok) {
        const blob = new Blob([data.data], { type: 'text/plain' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `conversation-${sessionId}.${format}`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
      }
    } catch (error) {
      console.error('Error exporting conversation:', error)
    }
  }

  const clearConversation = async () => {
    if (!sessionId) return

    try {
      await fetch(`${BACKEND_URL}/api/rag/clear/${sessionId}`, {
        method: 'DELETE'
      })
      setMessages([])
      setAgentStatus({})
    } catch (error) {
      console.error('Error clearing conversation:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processing': return 'text-blue-500'
      case 'completed': return 'text-green-500'
      case 'error': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high': return 'text-green-600'
      case 'medium': return 'text-yellow-600'
      case 'low': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getSystemStatusDisplay = () => {
    switch (systemStatus) {
      case 'healthy':
        return { text: 'System Ready', color: 'bg-green-500', icon: '✅' }
      case 'initializing':
        return { text: 'Initializing', color: 'bg-yellow-500', icon: '⏳' }
      case 'partial':
        return { text: 'Partial', color: 'bg-orange-500', icon: '⚠️' }
      case 'error':
        return { text: 'Error', color: 'bg-red-500', icon: '❌' }
      default:
        return { text: 'Unknown', color: 'bg-gray-500', icon: '❓' }
    }
  }

  const statusDisplay = getSystemStatusDisplay()

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Academic Management AI Assistant</h1>
          <div className="flex items-center space-x-4">
            <div className={`px-3 py-1 rounded text-sm flex items-center space-x-2 ${statusDisplay.color}`}>
              <span>{statusDisplay.icon}</span>
              <span>{statusDisplay.text}</span>
            </div>
            <button
              onClick={() => checkSystemStatus()}
              className="px-3 py-1 bg-white bg-opacity-20 rounded hover:bg-opacity-30 transition"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Connection Error Banner */}
      {connectionError && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-red-500 mr-2">⚠️</span>
              <span>{connectionError}</span>
            </div>
            <button
              onClick={() => checkSystemStatus()}
              className="text-red-700 hover:text-red-900 underline"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Agent Status */}
      {Object.keys(agentStatus).length > 0 && (
        <div className="bg-gray-50 p-3 border-b">
          <div className="flex space-x-4 text-sm">
            {Object.entries(agentStatus).map(([agent, status]) => (
              <div key={agent} className="flex items-center space-x-2">
                <span className="capitalize">{agent}:</span>
                <span className={getStatusColor(status)}>
                  {status === 'processing' && '⏳'}
                  {status === 'completed' && '✅'}
                  {status === 'error' && '❌'}
                  {status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold mb-2">Welcome to Academic Management AI</h3>
            <p className="text-sm">
              Ask me about academic policies, procedures, attendance, leave management, events, and more!
            </p>
            {systemStatus === 'error' && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-700 text-sm">
                  ⚠️ Backend connection issue detected. Please ensure the backend server is running on port 5001.
                </p>
              </div>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Message metadata */}
                <div className="mt-2 text-xs opacity-70">
                  {message.timestamp.toLocaleTimeString()}
                  {message.confidence && (
                    <span className={`ml-2 ${getConfidenceColor(message.confidence)}`}>
                      Confidence: {message.confidence}
                    </span>
                  )}
                </div>

                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <div className="text-xs text-gray-600 mb-1">Suggestions:</div>
                    <div className="flex flex-wrap gap-1">
                      {message.suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => setInputMessage(suggestion)}
                          className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200 transition"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>Processing your request...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about academic management..."
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={1}
            disabled={isLoading || systemStatus === 'error'}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim() || systemStatus === 'error'}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            Send
          </button>
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center mt-2 text-sm text-gray-600">
          <div className="flex space-x-2">
            <button
              onClick={() => exportConversation('json')}
              className="hover:text-blue-600 transition disabled:opacity-50"
              disabled={systemStatus === 'error'}
            >
              Export JSON
            </button>
            <button
              onClick={() => exportConversation('txt')}
              className="hover:text-blue-600 transition disabled:opacity-50"
              disabled={systemStatus === 'error'}
            >
              Export TXT
            </button>
          </div>
          <button
            onClick={clearConversation}
            className="text-red-600 hover:text-red-700 transition disabled:opacity-50"
            disabled={systemStatus === 'error'}
          >
            Clear Chat
          </button>
        </div>
      </div>
    </div>
  )
}
