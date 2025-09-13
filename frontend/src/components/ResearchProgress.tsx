'use client';

interface ResearchState {
  stage: string;
  progress: number;
  language: 'ko' | 'en';
  research_question: string;
  final_report?: string;
  error?: string;
}

interface ResearchProgressProps {
  currentState: ResearchState;
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
}

export default function ResearchProgress({ currentState, connectionStatus }: ResearchProgressProps) {
  const getStageInfo = (stage: string, language: 'ko' | 'en') => {
    const stages = {
      'idle': {
        ko: { title: '대기 중', description: '연구 준비 중입니다' },
        en: { title: 'Idle', description: 'Preparing for research' }
      },
      'initializing': {
        ko: { title: '초기화 중', description: '시스템을 초기화하고 있습니다' },
        en: { title: 'Initializing', description: 'Initializing the system' }
      },
      'clarifying': {
        ko: { title: '연구 계획 수립', description: '연구 목표를 명확히 하고 있습니다' },
        en: { title: 'Planning Research', description: 'Clarifying research objectives' }
      },
      'clarified': {
        ko: { title: '계획 완료', description: '연구 계획이 수립되었습니다' },
        en: { title: 'Planning Complete', description: 'Research plan established' }
      },
      'briefing': {
        ko: { title: '연구 브리프 작성', description: '상세한 연구 계획을 작성하고 있습니다' },
        en: { title: 'Creating Research Brief', description: 'Writing detailed research plan' }
      },
      'brief_complete': {
        ko: { title: '브리프 완료', description: '연구 브리프가 완성되었습니다' },
        en: { title: 'Brief Complete', description: 'Research brief completed' }
      },
      'planning': {
        ko: { title: '작업 분배', description: '연구 작업을 계획하고 있습니다' },
        en: { title: 'Task Planning', description: 'Planning research tasks' }
      },
      'research_planned': {
        ko: { title: '연구 시작 준비', description: '연구 작업이 배정되었습니다' },
        en: { title: 'Ready to Research', description: 'Research tasks assigned' }
      },
      'researching': {
        ko: { title: '연구 수행 중', description: '여러 연구원이 병렬로 조사하고 있습니다' },
        en: { title: 'Research in Progress', description: 'Multiple researchers working in parallel' }
      },
      'coordinating': {
        ko: { title: '연구 조율', description: '연구 진행 상황을 조율하고 있습니다' },
        en: { title: 'Coordinating Research', description: 'Coordinating research progress' }
      },
      'research_complete': {
        ko: { title: '연구 완료', description: '모든 연구 작업이 완료되었습니다' },
        en: { title: 'Research Complete', description: 'All research tasks completed' }
      },
      'synthesizing': {
        ko: { title: '내용 통합', description: '연구 결과를 종합하고 있습니다' },
        en: { title: 'Synthesizing Results', description: 'Integrating research findings' }
      },
      'synthesis_complete': {
        ko: { title: '통합 완료', description: '연구 결과가 통합되었습니다' },
        en: { title: 'Synthesis Complete', description: 'Research findings integrated' }
      },
      'finalizing': {
        ko: { title: '보고서 작성', description: '최종 보고서를 작성하고 있습니다' },
        en: { title: 'Creating Final Report', description: 'Generating final report' }
      },
      'completed': {
        ko: { title: '연구 완료!', description: '연구가 성공적으로 완료되었습니다' },
        en: { title: 'Research Complete!', description: 'Research completed successfully' }
      },
      'error': {
        ko: { title: '오류 발생', description: '연구 중 오류가 발생했습니다' },
        en: { title: 'Error Occurred', description: 'An error occurred during research' }
      }
    };

    const stageInfo = stages[stage as keyof typeof stages] || stages['idle'];
    return stageInfo[language] || stageInfo['en'];
  };

  const stageInfo = getStageInfo(currentState.stage, currentState.language);
  const isCompleted = currentState.stage === 'completed';
  const hasError = currentState.stage === 'error' || !!currentState.error;

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            연구 진행 상황 / Research Progress
          </h3>
          <div className="text-sm text-gray-600">
            <strong>질문 / Question:</strong> {currentState.research_question}
          </div>
        </div>
        
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          connectionStatus === 'connected' 
            ? 'bg-green-100 text-green-800' 
            : connectionStatus === 'connecting'
            ? 'bg-yellow-100 text-yellow-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {connectionStatus === 'connected' ? '실시간 연결 / Live' : 
           connectionStatus === 'connecting' ? '연결 중 / Connecting' : 
           '연결 끊김 / Disconnected'}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            {stageInfo.title}
          </span>
          <span className="text-sm text-gray-500">
            {currentState.progress}%
          </span>
        </div>
        
        <div className="progress-bar">
          <div 
            className={`progress-fill ${hasError ? 'bg-red-500' : isCompleted ? 'bg-green-500' : 'bg-blue-600'}`}
            style={{ width: `${Math.max(currentState.progress, 2)}%` }}
          />
        </div>
        
        <p className="text-sm text-gray-600 mt-2">
          {stageInfo.description}
        </p>
      </div>

      {/* Stage Indicators */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700 mb-3">
          연구 단계 / Research Stages
        </h4>
        
        {[
          { stage: 'clarifying', progress: 20 },
          { stage: 'briefing', progress: 40 },
          { stage: 'researching', progress: 70 },
          { stage: 'synthesizing', progress: 90 },
          { stage: 'completed', progress: 100 }
        ].map(({ stage, progress }) => {
          const info = getStageInfo(stage, currentState.language);
          const isCurrentStage = currentState.stage === stage || 
            (stage === 'researching' && currentState.stage.includes('research'));
          const isPassed = currentState.progress >= progress;
          const isCurrent = isCurrentStage && currentState.progress < 100;

          return (
            <div key={stage} className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full flex-shrink-0 ${
                hasError && isCurrent ? 'bg-red-500' :
                isPassed ? 'bg-green-500' : 
                isCurrent ? 'bg-blue-500 animate-pulse' : 
                'bg-gray-300'
              }`} />
              <span className={`text-sm ${
                isCurrent ? 'font-medium text-gray-900' : 
                isPassed ? 'text-gray-700' : 
                'text-gray-500'
              }`}>
                {info.title}
              </span>
            </div>
          );
        })}
      </div>

      {/* Error Display */}
      {hasError && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <h4 className="text-sm font-medium text-red-800 mb-2">
            오류 / Error
          </h4>
          <p className="text-sm text-red-700">
            {currentState.error || '연구 중 오류가 발생했습니다. Research error occurred.'}
          </p>
        </div>
      )}

      {/* Success Message */}
      {isCompleted && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <h4 className="text-sm font-medium text-green-800">
              {currentState.language === 'ko' ? '연구가 완료되었습니다!' : 'Research Completed!'}
            </h4>
          </div>
          <p className="text-sm text-green-700 mt-1">
            {currentState.language === 'ko' 
              ? '결과를 확인하려면 "결과 보기" 버튼을 클릭하세요.' 
              : 'Click "Show Results" to view the final report.'}
          </p>
        </div>
      )}

      {/* Loading Animation */}
      {!isCompleted && !hasError && (
        <div className="mt-6 flex items-center justify-center text-gray-500">
          <svg className="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-sm">
            {currentState.language === 'ko' ? '연구 진행 중...' : 'Research in progress...'}
          </span>
        </div>
      )}
    </div>
  );
}