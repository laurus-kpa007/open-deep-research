import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import DetailedProgress from './DetailedProgress';

const ResearchProgress = ({ sessionId, socket }) => {
  const [stage, setStage] = useState('');
  const [progress, setProgress] = useState(0);
  const [showDetails, setShowDetails] = useState(true);
  
  useEffect(() => {
    if (!socket || !sessionId) return;
    
    const handleProgress = (data) => {
      if (data.session_id === sessionId) {
        setStage(data.stage);
        setProgress(data.progress);
      }
    };
    
    socket.on('progress_update', handleProgress);
    
    return () => {
      socket.off('progress_update', handleProgress);
    };
  }, [socket, sessionId]);
  
  const getStageText = (stage) => {
    const stageMap = {
      'initializing': '초기화 중...',
      'clarifying': '연구 목표 분석 중...',
      'briefing': '연구 계획 수립 중...',
      'planning': '세부 작업 계획 중...',
      'researching': '연구 수행 중...',
      'synthesizing': '결과 통합 중...',
      'finalizing': '최종 보고서 작성 중...',
      'completed': '완료!'
    };
    return stageMap[stage] || stage;
  };
  
  return (
    <div className="space-y-6">
      {/* Main Progress Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">
            {getStageText(stage)}
          </h2>
          <span className="text-2xl font-bold text-blue-600">
            {progress}%
          </span>
        </div>
        
        <div className="relative">
          <div className="w-full bg-gray-200 rounded-full h-4">
            <motion.div
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-4 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
        
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="mt-4 text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          {showDetails ? '상세 정보 숨기기' : '상세 정보 보기'}
        </button>
      </div>
      
      {/* Detailed Progress Component */}
      {showDetails && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <DetailedProgress sessionId={sessionId} socket={socket} />
        </motion.div>
      )}
    </div>
  );
};

export default ResearchProgress;