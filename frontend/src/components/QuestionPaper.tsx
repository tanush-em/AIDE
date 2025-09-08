'use client'

import { useState } from 'react'
import { FileText, ExternalLink, Download, Settings, BookOpen, Clock, Users } from 'lucide-react'

export default function QuestionPaper() {
  const [isRedirecting, setIsRedirecting] = useState(false)

  const handleRedirect = () => {
    setIsRedirecting(true)
    // Open the external question paper application in a new tab
    window.open('http://localhost:5890', '_blank')
    // Reset the redirecting state after a short delay
    setTimeout(() => setIsRedirecting(false), 1000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center space-x-3">
          <div className="bg-purple-100 p-3 rounded-lg">
            <FileText className="h-6 w-6 text-purple-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Question Paper Generator</h1>
            <p className="text-gray-600">Generate and manage question papers for your courses</p>
          </div>
        </div>
      </div>

      {/* Main Action Card */}
      <div className="bg-white rounded-lg shadow-sm border p-8">
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mb-4">
            <FileText className="h-8 w-8 text-purple-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Question Paper Generator</h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Click the button below to open the Question Paper Generator application in a new tab. 
            You can create, edit, and manage question papers for all your courses.
          </p>
          
          <button
            onClick={handleRedirect}
            disabled={isRedirecting}
            className={`inline-flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
              isRedirecting
                ? 'bg-gray-400 text-white cursor-not-allowed'
                : 'bg-purple-600 text-white hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2'
            }`}
          >
            {isRedirecting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Opening...</span>
              </>
            ) : (
              <>
                <ExternalLink className="h-4 w-4" />
                <span>Open Question Paper Generator</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <BookOpen className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Course Integration</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Generate question papers based on your course curriculum and learning objectives.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <Clock className="h-5 w-5 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Time Management</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Set time limits and difficulty levels for different sections of your question papers.
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center space-x-3 mb-3">
            <div className="bg-orange-100 p-2 rounded-lg">
              <Users className="h-5 w-5 text-orange-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Student Focused</h3>
          </div>
          <p className="text-gray-600 text-sm">
            Create question papers tailored to your students' learning levels and assessment needs.
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={handleRedirect}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="bg-purple-100 p-2 rounded-lg">
              <FileText className="h-5 w-5 text-purple-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Create New Paper</p>
              <p className="text-sm text-gray-600">Start with a blank template</p>
            </div>
          </button>

          <button
            onClick={handleRedirect}
            className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="bg-blue-100 p-2 rounded-lg">
              <Download className="h-5 w-5 text-blue-600" />
            </div>
            <div className="text-left">
              <p className="font-medium text-gray-900">Download Templates</p>
              <p className="text-sm text-gray-600">Use pre-made question formats</p>
            </div>
          </button>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
        <div className="flex items-start space-x-3">
          <div className="bg-blue-100 p-2 rounded-lg">
            <Settings className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">Need Help?</h3>
            <p className="text-blue-800 text-sm mb-3">
              The Question Paper Generator runs as a separate application. If you encounter any issues:
            </p>
            <ul className="text-blue-800 text-sm space-y-1">
              <li>• Ensure the application is running on localhost:5890</li>
              <li>• Check your browser's popup blocker settings</li>
              <li>• Contact IT support if the application doesn't load</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
