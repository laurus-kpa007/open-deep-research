'use client';

import { useQuery } from '@tanstack/react-query';
import { researchApi } from '@/lib/api';

export default function HealthCheck() {
  const { data: healthData, isLoading, error } = useQuery({
    queryKey: ['health'],
    queryFn: researchApi.healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
    retry: 3,
  });

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center space-x-3">
          <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="text-sm text-gray-600">
            시스템 상태 확인 중... / Checking system status...
          </span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card border-red-200 bg-red-50">
        <div className="flex items-center space-x-3">
          <div className="w-5 h-5 bg-red-500 rounded-full flex-shrink-0"></div>
          <div>
            <h3 className="font-medium text-red-800">
              시스템 연결 오류 / System Connection Error
            </h3>
            <p className="text-sm text-red-700 mt-1">
              백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.
              <br />
              Cannot connect to backend server. Please check if the server is running.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const isHealthy = healthData?.status === 'healthy';
  const ollamaAvailable = healthData?.ollama_available;
  const searchAvailable = healthData?.search_available;

  return (
    <div className={`card ${isHealthy ? 'border-green-200 bg-green-50' : 'border-yellow-200 bg-yellow-50'}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
          <div>
            <h3 className={`font-medium ${isHealthy ? 'text-green-800' : 'text-yellow-800'}`}>
              시스템 상태 / System Status
            </h3>
            <div className="mt-2 space-y-1 text-sm">
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${ollamaAvailable ? 'bg-green-400' : 'bg-red-400'}`}></span>
                <span className={ollamaAvailable ? 'text-green-700' : 'text-red-700'}>
                  Ollama LLM: {ollamaAvailable ? '연결됨 / Connected' : '연결 안됨 / Disconnected'}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <span className={`w-2 h-2 rounded-full ${searchAvailable ? 'bg-green-400' : 'bg-red-400'}`}></span>
                <span className={searchAvailable ? 'text-green-700' : 'text-red-700'}>
                  Search API: {searchAvailable ? '사용 가능 / Available' : '사용 불가 / Unavailable'}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="text-xs text-gray-500">
          마지막 확인 / Last check: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {!ollamaAvailable && (
        <div className="mt-4 p-3 bg-amber-100 border border-amber-200 rounded-lg">
          <p className="text-sm text-amber-800">
            <strong>⚠️ Ollama 연결 안됨 / Ollama Not Connected:</strong><br />
            Ollama 서버를 시작하고 gemma2:12b 모델이 설치되어 있는지 확인하세요.
            <br />
            Please start Ollama server and ensure gemma2:12b model is installed.
          </p>
          <div className="mt-2 text-xs text-amber-700 font-mono">
            <div>$ ollama serve</div>
            <div>$ ollama pull gemma2:12b</div>
          </div>
        </div>
      )}

      {!searchAvailable && (
        <div className="mt-4 p-3 bg-blue-100 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>ℹ️ 검색 API 사용 불가 / Search API Unavailable:</strong><br />
            Tavily API 키가 설정되지 않았습니다. 검색 기능이 제한됩니다.
            <br />
            Tavily API key not configured. Search functionality will be limited.
          </p>
        </div>
      )}
    </div>
  );
}