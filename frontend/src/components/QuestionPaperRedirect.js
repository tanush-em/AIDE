'use client'

import { ExternalLink, FileText, ArrowRight } from 'lucide-react'

export default function QuestionPaperRedirect() {
  const handleRedirect = () => {
    // Open the external question paper application in a new tab
    window.open('http://localhost:5890', '_blank')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className="bg-blue-100 p-4 rounded-full w-20 h-20 mx-auto mb-4 flex items-center justify-center">
          <FileText className="h-10 w-10 text-blue-600" />
        </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Question Paper Generator</h2>
        <p className="text-lg text-gray-600 mb-8">
          Access our advanced question paper generation tool to create comprehensive examination papers
        </p>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg border p-8 text-center">
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-3">
              Ready to Generate Question Papers?
            </h3>
            <p className="text-gray-600 mb-6">
              Our dedicated question paper generation application provides advanced features for creating, 
              customizing, and managing examination papers with ease.
            </p>
          </div>

          {/* Features List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8 text-left">
            <div className="flex items-start space-x-3">
              <div className="bg-green-100 p-1 rounded-full mt-1">
                <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Smart Question Generation</h4>
                <p className="text-sm text-gray-600">AI-powered question creation</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-green-100 p-1 rounded-full mt-1">
                <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Multiple Formats</h4>
                <p className="text-sm text-gray-600">PDF, Word, and online formats</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-green-100 p-1 rounded-full mt-1">
                <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Custom Templates</h4>
                <p className="text-sm text-gray-600">Pre-built and custom layouts</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-green-100 p-1 rounded-full mt-1">
                <div className="w-2 h-2 bg-green-600 rounded-full"></div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Difficulty Control</h4>
                <p className="text-sm text-gray-600">Adjustable complexity levels</p>
              </div>
            </div>
          </div>

          {/* Redirect Button */}
          <button
            onClick={handleRedirect}
            className="inline-flex items-center space-x-3 px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-lg font-medium shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200"
          >
            <ExternalLink className="h-6 w-6" />
            <span>Open Question Paper Generator</span>
            <ArrowRight className="h-5 w-5" />
          </button>

          <p className="text-sm text-gray-500 mt-4">
            The application will open in a new tab
          </p>
        </div>

        {/* Additional Info */}
        <div className="mt-8 bg-gray-50 rounded-lg p-6">
          <h4 className="font-medium text-gray-900 mb-3">Need Help?</h4>
          <p className="text-sm text-gray-600 mb-4">
            If you're having trouble accessing the question paper generator, please ensure that:
          </p>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• The question paper application is running on localhost:5890</li>
            <li>• Your browser allows pop-ups for this site</li>
            <li>• You have the necessary permissions to access the application</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
