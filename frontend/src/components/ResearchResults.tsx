'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ResearchReport {
  session_id: string;
  report: string;
  language: 'ko' | 'en';
  research_question: string;
  sources: string[][];
  generated_at?: string;
}

interface ResearchResultsProps {
  report: ResearchReport;
  onClose: () => void;
}

export default function ResearchResults({ report, onClose }: ResearchResultsProps) {
  const [activeTab, setActiveTab] = useState<'report' | 'sources'>('report');

  const handleDownload = (format: 'markdown' | 'text') => {
    const content = format === 'markdown' ? report.report : report.report.replace(/[#*`]/g, '');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-report-${report.session_id.slice(0, 8)}.${format === 'markdown' ? 'md' : 'txt'}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(report.report);
      // You could add a toast notification here
      alert(report.language === 'ko' ? '보고서가 클립보드에 복사되었습니다.' : 'Report copied to clipboard.');
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const flatSources = report.sources.flat().filter(Boolean);
  const uniqueSources = Array.from(new Set(flatSources));

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          <h2 className="text-xl font-bold text-gray-900 mb-2">
            연구 결과 / Research Results
          </h2>
          <div className="text-sm text-gray-600">
            <div><strong>질문 / Question:</strong> {report.research_question}</div>
            <div><strong>언어 / Language:</strong> {report.language === 'ko' ? '한국어' : 'English'}</div>
            {report.generated_at && (
              <div><strong>생성 시간 / Generated:</strong> {new Date(report.generated_at).toLocaleString()}</div>
            )}
          </div>
        </div>
        
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={handleCopy}
          className="btn-secondary text-sm"
        >
          📋 {report.language === 'ko' ? '복사' : 'Copy'}
        </button>
        
        <button
          onClick={() => handleDownload('markdown')}
          className="btn-secondary text-sm"
        >
          📄 {report.language === 'ko' ? 'Markdown 다운로드' : 'Download Markdown'}
        </button>
        
        <button
          onClick={() => handleDownload('text')}
          className="btn-secondary text-sm"
        >
          📝 {report.language === 'ko' ? '텍스트 다운로드' : 'Download Text'}
        </button>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('report')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'report'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            보고서 / Report
          </button>
          
          <button
            onClick={() => setActiveTab('sources')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'sources'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            출처 / Sources ({uniqueSources.length})
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="fade-in">
        {activeTab === 'report' ? (
          <div className="prose max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {report.report}
            </ReactMarkdown>
          </div>
        ) : (
          <div>
            <h3 className="text-lg font-semibold mb-4">
              {report.language === 'ko' ? '참고 자료' : 'Reference Sources'}
            </h3>
            
            {uniqueSources.length > 0 ? (
              <div className="space-y-3">
                {uniqueSources.map((source, index) => (
                  <div
                    key={index}
                    className="p-3 bg-gray-50 rounded-lg border"
                  >
                    <div className="flex items-start space-x-3">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-800 text-xs font-medium rounded-full flex items-center justify-center">
                        {index + 1}
                      </span>
                      <div className="flex-1">
                        {source.startsWith('http') ? (
                          <a
                            href={source}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 underline break-all"
                          >
                            {source}
                          </a>
                        ) : (
                          <span className="text-gray-700 break-all">{source}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 italic">
                {report.language === 'ko' 
                  ? '참고 자료가 없습니다.' 
                  : 'No sources available.'}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div>
            Session ID: {report.session_id}
          </div>
          <div>
            Deep Research Agent v0.1.0
          </div>
        </div>
      </div>
    </div>
  );
}