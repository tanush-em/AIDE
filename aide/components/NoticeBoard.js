'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bell, 
  Pin, 
  AlertTriangle, 
  Info, 
  Clock,
  User,
  Calendar,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export default function NoticeBoard() {
  const [notices, setNotices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedNotice, setExpandedNotice] = useState(null);

  useEffect(() => {
    fetchNotices();
  }, []);

  const fetchNotices = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/notices');
      if (response.ok) {
        const data = await response.json();
        // Sort notices: pinned first, then by priority, then by date
        const sortedNotices = data.sort((a, b) => {
          if (a.pinned && !b.pinned) return -1;
          if (!a.pinned && b.pinned) return 1;
          
          const priorityOrder = { 'critical': 3, 'high': 2, 'low': 1 };
          const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
          if (priorityDiff !== 0) return priorityDiff;
          
          return new Date(b.posted_date) - new Date(a.posted_date);
        });
        setNotices(sortedNotices);
      }
    } catch (error) {
      console.error('Error fetching notices:', error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'bg-red-500';
      case 'high': return 'bg-orange-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical': return AlertTriangle;
      case 'high': return Info;
      case 'low': return Info;
      default: return Info;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const renderMarkdownContent = (content) => {
    // Simple markdown rendering for bold and line breaks
    return content
      .split('\n')
      .map((line, index) => {
        if (line.trim() === '') return <br key={index} />;
        
        const parts = line.split('**');
        const elements = parts.map((part, partIndex) => {
          if (partIndex % 2 === 1) {
            return <strong key={partIndex}>{part}</strong>;
          }
          return part;
        });
        
        return <p key={index} className="mb-2">{elements}</p>;
      });
  };

  if (loading) {
    return (
      <div className="bg-white dark:bg-slate-800 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-center h-32">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 px-6 py-4 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <Bell className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">
                Notice Board
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {notices.length} notices posted
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Notices List */}
      <div className="max-h-96 overflow-y-auto">
        <AnimatePresence>
          {notices.map((notice, index) => (
            <motion.div
              key={notice.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`border-b border-slate-200 dark:border-slate-700 last:border-b-0 ${
                notice.pinned ? 'bg-yellow-50 dark:bg-yellow-900/10' : ''
              }`}
            >
              <div className="p-4 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                {/* Notice Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-start space-x-3 flex-1">
                    {/* Priority Indicator */}
                    <div className={`w-3 h-3 rounded-full ${getPriorityColor(notice.priority)} mt-1`}></div>
                    
                    {/* Title and Meta */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className="font-semibold text-slate-800 dark:text-slate-200 truncate">
                          {notice.title}
                        </h3>
                        {notice.pinned && (
                          <Pin className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                        )}
                      </div>
                      
                      {/* Meta Information */}
                      <div className="flex items-center space-x-4 text-xs text-slate-500 dark:text-slate-400">
                        <div className="flex items-center space-x-1">
                          <User className="w-3 h-3" />
                          <span>{notice.posted_by}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(notice.posted_date)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span className="capitalize">{notice.priority} priority</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* Expand/Collapse Button */}
                  <button
                    onClick={() => setExpandedNotice(expandedNotice === notice.id ? null : notice.id)}
                    className="p-1 hover:bg-slate-200 dark:hover:bg-slate-600 rounded transition-colors"
                  >
                    {expandedNotice === notice.id ? (
                      <ChevronUp className="w-4 h-4 text-slate-500" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-500" />
                    )}
                  </button>
                </div>

                {/* Notice Content */}
                <AnimatePresence>
                  {expandedNotice === notice.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden"
                    >
                      <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 mt-3">
                        <div className="prose prose-sm max-w-none text-slate-700 dark:text-slate-300">
                          {renderMarkdownContent(notice.content)}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {notices.length === 0 && (
          <div className="p-8 text-center">
            <Bell className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <p className="text-slate-500 dark:text-slate-400">No notices available</p>
          </div>
        )}
      </div>
    </motion.div>
  );
} 