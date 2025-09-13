'use client';

import { useState } from 'react';
import { ChevronDownIcon } from '@heroicons/react/20/solid';

interface ResearchFormProps {
  onSubmit: (query: string, options: any) => void;
  isLoading: boolean;
  disabled: boolean;
}

export default function ResearchForm({ onSubmit, isLoading, disabled }: ResearchFormProps) {
  const [query, setQuery] = useState('');
  const [language, setLanguage] = useState<'auto' | 'ko' | 'en'>('auto');
  const [depth, setDepth] = useState<'shallow' | 'medium' | 'deep'>('deep');
  const [maxResearchers, setMaxResearchers] = useState(5);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !disabled) {
      onSubmit(query.trim(), {
        language: language === 'auto' ? undefined : language,
        depth,
        max_researchers: maxResearchers,
      });
    }
  };

  const exampleQueries = [
    {
      ko: "AI 기술의 최신 동향과 미래 전망",
      en: "Latest trends and future prospects of AI technology"
    },
    {
      ko: "기후변화가 농업에 미치는 영향",
      en: "Impact of climate change on agriculture"
    },
    {
      ko: "양자 컴퓨팅의 현재 상황과 응용 분야",
      en: "Current state and applications of quantum computing"
    }
  ];

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-2">
          연구 시작하기 / Start Research
        </h2>
        <p className="text-sm text-gray-600">
          연구하고 싶은 주제를 입력하세요
          <br />
          Enter the topic you want to research
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Query Input */}
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
            연구 질문 / Research Question
          </label>
          <textarea
            id="query"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="예: AI 기술의 최신 동향&#10;Example: Latest trends in AI technology"
            className="input-field min-h-[100px] resize-none"
            disabled={disabled}
            maxLength={1000}
          />
          <div className="mt-1 text-xs text-gray-500">
            {query.length}/1000
          </div>
        </div>

        {/* Example Queries */}
        <div>
          <p className="text-xs text-gray-600 mb-2">예시 질문 / Example queries:</p>
          <div className="space-y-1">
            {exampleQueries.map((example, index) => (
              <button
                key={index}
                type="button"
                onClick={() => setQuery(example.ko)}
                className="text-left text-xs text-blue-600 hover:text-blue-800 block w-full truncate"
                disabled={disabled}
              >
                • {example.ko}
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Options Toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center text-sm text-gray-600 hover:text-gray-800"
          disabled={disabled}
        >
          <ChevronDownIcon 
            className={`w-4 h-4 mr-1 transform transition-transform ${showAdvanced ? 'rotate-180' : ''}`}
          />
          고급 설정 / Advanced Settings
        </button>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-4 pt-2 border-t border-gray-200">
            {/* Language Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                언어 / Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value as any)}
                className="input-field"
                disabled={disabled}
              >
                <option value="auto">자동 감지 / Auto Detect</option>
                <option value="ko">한국어 / Korean</option>
                <option value="en">English</option>
              </select>
            </div>

            {/* Research Depth */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                연구 깊이 / Research Depth
              </label>
              <select
                value={depth}
                onChange={(e) => setDepth(e.target.value as any)}
                className="input-field"
                disabled={disabled}
              >
                <option value="shallow">간단 / Shallow</option>
                <option value="medium">보통 / Medium</option>
                <option value="deep">심층 / Deep</option>
              </select>
              <p className="mt-1 text-xs text-gray-500">
                심층 연구일수록 더 많은 시간이 소요됩니다
                <br />
                Deeper research takes more time
              </p>
            </div>

            {/* Max Researchers */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                동시 연구원 수 / Concurrent Researchers: {maxResearchers}
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={maxResearchers}
                onChange={(e) => setMaxResearchers(Number(e.target.value))}
                className="w-full"
                disabled={disabled}
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>1 (빠름 / Fast)</span>
                <span>5 (포괄적 / Comprehensive)</span>
              </div>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!query.trim() || isLoading || disabled}
          className={`w-full btn-primary relative ${
            (isLoading || disabled) ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              연구 시작 중... / Starting Research...
            </span>
          ) : (
            <span>연구 시작 / Start Research</span>
          )}
        </button>

        {/* Disabled Message */}
        {disabled && !isLoading && (
          <p className="text-xs text-center text-amber-600 bg-amber-50 py-2 px-3 rounded">
            연구가 진행 중입니다. 완료 후 새 연구를 시작할 수 있습니다.
            <br />
            Research in progress. You can start a new research after completion.
          </p>
        )}
      </form>
    </div>
  );
}