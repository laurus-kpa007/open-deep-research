'use client';

import { useState } from 'react';
import { useResearchSession } from '@/hooks/useResearchSession';
import ResearchForm from '@/components/ResearchForm';
import ResearchProgress from '@/components/ResearchProgress';
import ResearchResults from '@/components/ResearchResults';
import HealthCheck from '@/components/HealthCheck';

export default function HomePage() {
  const {
    sessionId,
    currentState,
    startResearch,
    isStarting,
    resetSession,
    connectionStatus,
    reportData,
  } = useResearchSession();

  const [showResults, setShowResults] = useState(false);

  const handleStartResearch = (query: string, options: any) => {
    setShowResults(false);
    startResearch({
      query,
      ...options,
    });
  };

  const handleShowResults = () => {
    setShowResults(true);
  };

  const handleReset = () => {
    setShowResults(false);
    resetSession();
  };

  return (
    <div className="space-y-8">
      {/* Health Check */}
      <HealthCheck />

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Panel - Research Form */}
        <div className="lg:col-span-1">
          <div className="sticky top-4">
            <ResearchForm
              onSubmit={handleStartResearch}
              isLoading={isStarting}
              disabled={!!sessionId && currentState.stage !== 'completed' && currentState.stage !== 'error'}
            />
            
            {sessionId && (
              <div className="mt-6 card">
                <h3 className="text-lg font-semibold mb-4">세션 정보 / Session Info</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="font-medium">ID:</span>
                    <span className="ml-2 font-mono text-xs">{sessionId}</span>
                  </div>
                  <div>
                    <span className="font-medium">언어 / Language:</span>
                    <span className="ml-2">{currentState.language === 'ko' ? '한국어' : 'English'}</span>
                  </div>
                  <div>
                    <span className="font-medium">상태 / Status:</span>
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                      connectionStatus === 'connected' 
                        ? 'bg-green-100 text-green-800' 
                        : connectionStatus === 'connecting'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {connectionStatus === 'connected' ? '연결됨 / Connected' : 
                       connectionStatus === 'connecting' ? '연결중 / Connecting' : 
                       '연결끊김 / Disconnected'}
                    </span>
                  </div>
                </div>
                
                <div className="mt-4 space-y-2">
                  {currentState.stage === 'completed' && (
                    <button
                      onClick={handleShowResults}
                      className="w-full btn-primary"
                    >
                      {currentState.language === 'ko' ? '결과 보기' : 'Show Results'}
                    </button>
                  )}
                  <button
                    onClick={handleReset}
                    className="w-full btn-secondary"
                  >
                    {currentState.language === 'ko' ? '새 연구 시작' : 'Start New Research'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Progress and Results */}
        <div className="lg:col-span-2">
          {sessionId && !showResults && (
            <ResearchProgress
              currentState={currentState}
              connectionStatus={connectionStatus}
            />
          )}

          {showResults && reportData && (
            <ResearchResults
              report={reportData}
              onClose={() => setShowResults(false)}
            />
          )}

          {/* Welcome Message */}
          {!sessionId && (
            <div className="card text-center">
              <div className="max-w-2xl mx-auto">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Deep Research Agent에 오신 것을 환영합니다
                </h2>
                <h3 className="text-xl text-gray-600 mb-6">
                  Welcome to Deep Research Agent
                </h3>
                
                <div className="text-left space-y-4 text-gray-700">
                  <div className="border-l-4 border-blue-400 pl-4">
                    <h4 className="font-semibold mb-2">🧠 AI 기반 심층 연구 / AI-Powered Deep Research</h4>
                    <p className="text-sm">
                      Ollama를 활용한 로컬 LLM으로 프라이버시를 보장하면서 고품질 연구를 수행합니다.
                      <br />
                      Conduct high-quality research while ensuring privacy with local LLM via Ollama.
                    </p>
                  </div>
                  
                  <div className="border-l-4 border-green-400 pl-4">
                    <h4 className="font-semibold mb-2">🌐 다국어 지원 / Multilingual Support</h4>
                    <p className="text-sm">
                      한국어와 영어로 질문하고 같은 언어로 답변을 받을 수 있습니다.
                      <br />
                      Ask questions in Korean or English and receive responses in the same language.
                    </p>
                  </div>
                  
                  <div className="border-l-4 border-purple-400 pl-4">
                    <h4 className="font-semibold mb-2">⚡ 실시간 진행상황 / Real-time Progress</h4>
                    <p className="text-sm">
                      연구 진행 과정을 실시간으로 모니터링할 수 있습니다.
                      <br />
                      Monitor the research progress in real-time with live updates.
                    </p>
                  </div>
                  
                  <div className="border-l-4 border-orange-400 pl-4">
                    <h4 className="font-semibold mb-2">📊 포괄적 보고서 / Comprehensive Reports</h4>
                    <p className="text-sm">
                      다양한 소스를 종합하여 구조화된 고품질 연구 보고서를 생성합니다.
                      <br />
                      Generate structured, high-quality research reports from multiple sources.
                    </p>
                  </div>
                </div>
                
                <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    💡 <strong>시작하려면:</strong> 왼쪽 폼에 연구하고 싶은 주제를 입력하세요.
                    <br />
                    💡 <strong>To get started:</strong> Enter your research topic in the form on the left.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}