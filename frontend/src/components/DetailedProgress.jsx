import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  SearchIcon,
  BrainIcon,
  WriteIcon,
  LinkIcon,
  CheckCircleIcon,
  LoaderIcon,
  FileTextIcon,
  DatabaseIcon
} from 'lucide-react';

const DetailedProgress = ({ sessionId, socket }) => {
  const [progressItems, setProgressItems] = useState([]);
  const [currentThoughts, setCurrentThoughts] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [draftContent, setDraftContent] = useState('');
  const [researchTasks, setResearchTasks] = useState([]);
  
  useEffect(() => {
    if (!socket || !sessionId) return;
    
    // Listen for detailed progress updates
    const handleProgressUpdate = (data) => {
      if (data.detailed) {
        setProgressItems(prev => [...prev.slice(-20), data.detailed]);
      }
      
      if (data.current_search_results) {
        setSearchResults(data.current_search_results);
      }
      
      if (data.draft_content) {
        setDraftContent(data.draft_content);
      }
    };
    
    const handleThinking = (data) => {
      setCurrentThoughts(data.message);
    };
    
    const handleSearching = (data) => {
      setProgressItems(prev => [...prev, {
        type: 'searching',
        message: data.message,
        sources_found: data.sources_found
      }]);
    };
    
    socket.on('progress_update', handleProgressUpdate);
    socket.on('progress_thinking', handleThinking);
    socket.on('progress_searching', handleSearching);
    
    return () => {
      socket.off('progress_update', handleProgressUpdate);
      socket.off('progress_thinking', handleThinking);
      socket.off('progress_searching', handleSearching);
    };
  }, [socket, sessionId]);
  
  const getIcon = (type) => {
    switch(type) {
      case 'thinking': return <BrainIcon className="w-5 h-5" />;
      case 'searching': return <SearchIcon className="w-5 h-5" />;
      case 'analyzing': return <DatabaseIcon className="w-5 h-5" />;
      case 'writing': return <WriteIcon className="w-5 h-5" />;
      case 'synthesizing': return <LinkIcon className="w-5 h-5" />;
      case 'validating': return <CheckCircleIcon className="w-5 h-5" />;
      case 'formatting': return <FileTextIcon className="w-5 h-5" />;
      default: return <LoaderIcon className="w-5 h-5 animate-spin" />;
    }
  };
  
  const getTypeColor = (type) => {
    switch(type) {
      case 'thinking': return 'text-purple-600 bg-purple-50';
      case 'searching': return 'text-blue-600 bg-blue-50';
      case 'analyzing': return 'text-indigo-600 bg-indigo-50';
      case 'writing': return 'text-green-600 bg-green-50';
      case 'synthesizing': return 'text-orange-600 bg-orange-50';
      case 'validating': return 'text-teal-600 bg-teal-50';
      case 'formatting': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Current Activity Stream */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">실시간 진행 상황</h3>
        
        <div className="space-y-3 max-h-96 overflow-y-auto">
          <AnimatePresence>
            {progressItems.slice(-10).map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`flex items-start space-x-3 p-3 rounded-lg ${getTypeColor(item.type)}`}
              >
                <div className="flex-shrink-0 mt-1">
                  {getIcon(item.type)}
                </div>
                <div className="flex-1">
                  <p className="font-medium">{item.message}</p>
                  {item.details && (
                    <p className="text-sm mt-1 opacity-75">{item.details}</p>
                  )}
                  {item.sources_found && (
                    <p className="text-sm mt-1">
                      <span className="font-semibold">{item.sources_found}</span>개의 소스 발견
                    </p>
                  )}
                  {item.current_item && item.total_items && (
                    <div className="mt-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span>작업 진행도</span>
                        <span>{item.current_item}/{item.total_items}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(item.current_item / item.total_items) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
      
      {/* Search Results Preview */}
      {searchResults.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">검색 결과</h3>
          <div className="space-y-2">
            {searchResults.slice(0, 5).map((result, index) => (
              <div key={index} className="flex items-start space-x-2 p-2 hover:bg-gray-50 rounded">
                <span className="text-blue-500 mt-1">
                  <LinkIcon className="w-4 h-4" />
                </span>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{result.title}</p>
                  <p className="text-xs text-gray-500 truncate">{result.url}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Draft Content Preview */}
      {draftContent && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">작성 중인 내용 미리보기</h3>
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-600 leading-relaxed">
              {draftContent.slice(-500)}
              {draftContent.length > 500 && '...'}
            </p>
          </div>
        </div>
      )}
      
      {/* Research Tasks Progress */}
      {researchTasks.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">연구 작업 진행도</h3>
          <div className="space-y-2">
            {researchTasks.map((task, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                  task.completed ? 'bg-green-100' : 'bg-gray-100'
                }`}>
                  {task.completed ? (
                    <CheckCircleIcon className="w-4 h-4 text-green-600" />
                  ) : (
                    <span className="text-xs text-gray-600">{index + 1}</span>
                  )}
                </div>
                <p className={`text-sm ${task.completed ? 'text-gray-500 line-through' : 'text-gray-800'}`}>
                  {task.question}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DetailedProgress;