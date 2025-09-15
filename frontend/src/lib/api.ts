import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Type definitions
export interface ResearchRequest {
  query: string;
  language?: 'ko' | 'en';
  depth?: 'shallow' | 'medium' | 'deep';
  max_researchers?: number;
}

export interface ResearchResponse {
  session_id: string;
  status: string;
  language: 'ko' | 'en';
  message: string;
}

export interface ResearchStatus {
  session_id: string;
  stage: string;
  progress: number;
  language: 'ko' | 'en';
  research_question: string;
  final_report?: string;
  created_at?: string;
  last_updated?: string;
}

export interface ResearchReport {
  session_id: string;
  report: string;
  language: 'ko' | 'en';
  research_question: string;
  sources: string[][];
  generated_at?: string;
}

export interface HealthStatus {
  status: string;
  ollama_available: boolean;
  search_available: boolean;
}

// API methods
export const researchApi = {
  // Health check
  async healthCheck(): Promise<HealthStatus> {
    const response = await apiClient.get('/api/v1/health');
    return response.data;
  },

  // Start research
  async startResearch(request: ResearchRequest): Promise<ResearchResponse> {
    const response = await apiClient.post('/api/v1/research/start', request);
    return response.data;
  },

  // Get research status
  async getResearchStatus(sessionId: string): Promise<ResearchStatus> {
    const response = await apiClient.get(`/api/v1/research/${sessionId}`);
    return response.data;
  },

  // Get research report
  async getResearchReport(sessionId: string): Promise<ResearchReport> {
    const response = await apiClient.get(`/api/v1/research/${sessionId}/report`);
    return response.data;
  },
};

export default apiClient;