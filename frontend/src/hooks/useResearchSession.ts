'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import toast from 'react-hot-toast';
import { researchApi } from '@/lib/api';

export interface ResearchState {
  session_id: string;
  stage: string;
  progress: number;
  language: 'ko' | 'en';
  research_question: string;
  final_report?: string;
  created_at?: string;
  last_updated?: string;
  error?: string;
}

export interface ResearchProgress {
  type: string;
  session_id: string;
  stage: string;
  progress: number;
  data?: any;
  timestamp: string;
  error?: string;
}

export interface ResearchRequest {
  query: string;
  language?: 'ko' | 'en';
  depth?: 'shallow' | 'medium' | 'deep';
  max_researchers?: number;
}

export function useResearchSession() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [realTimeProgress, setRealTimeProgress] = useState<ResearchProgress | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const queryClient = useQueryClient();
  const socketRef = useRef<Socket | null>(null);

  // Fetch session status
  const { data: sessionData, error: sessionError, isLoading: sessionLoading } = useQuery({
    queryKey: ['research-session', sessionId],
    queryFn: () => sessionId ? researchApi.getResearchStatus(sessionId) : null,
    enabled: !!sessionId,
    refetchInterval: (query) => {
      // Stop polling if completed or error
      if (query.state.data?.stage === 'completed' || query.state.data?.stage === 'error') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });

  // Fetch final report
  const { data: reportData } = useQuery({
    queryKey: ['research-report', sessionId],
    queryFn: () => sessionId ? researchApi.getResearchReport(sessionId) : null,
    enabled: !!sessionId && sessionData?.stage === 'completed',
  });

  // Start research mutation
  const startResearchMutation = useMutation({
    mutationFn: (request: ResearchRequest) => researchApi.startResearch(request),
    onSuccess: (response) => {
      setSessionId(response.session_id);
      toast.success(
        response.language === 'ko' 
          ? '연구가 시작되었습니다!' 
          : 'Research started successfully!'
      );
      
      // Connect to WebSocket and Socket.IO
      connectToRealTime(response.session_id);
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Failed to start research';
      toast.error(message);
    },
  });

  const connectToRealTime = (sessionId: string) => {
    setConnectionStatus('connecting');
    
    // Socket.IO connection
    const newSocket = io(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000', {
      transports: ['websocket', 'polling'],
      timeout: 10000,
    });

    socketRef.current = newSocket;
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Socket.IO connected');
      setConnectionStatus('connected');
      
      // Join the session room
      newSocket.emit('join_session', { session_id: sessionId });
    });

    newSocket.on('disconnect', () => {
      console.log('Socket.IO disconnected');
      setConnectionStatus('disconnected');
    });

    newSocket.on('progress_update', (progress: ResearchProgress) => {
      console.log('Progress update:', progress);
      setRealTimeProgress(progress);
      
      // Update query cache
      queryClient.setQueryData(['research-session', sessionId], (old: any) => {
        if (!old) return old;
        return {
          ...old,
          stage: progress.stage,
          progress: progress.progress,
          final_report: progress.data?.final_report || old.final_report,
        };
      });
      
      // Show progress toasts
      if (progress.stage === 'completed') {
        toast.success(
          progress.data?.language === 'ko' 
            ? '연구가 완료되었습니다!' 
            : 'Research completed successfully!'
        );
      } else if (progress.error) {
        toast.error(progress.error);
      }
    });

    newSocket.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error);
      setConnectionStatus('disconnected');
      toast.error('Failed to connect to real-time updates');
    });
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  // Reset function
  const resetSession = () => {
    setSessionId(null);
    setRealTimeProgress(null);
    if (socketRef.current) {
      socketRef.current.disconnect();
      setSocket(null);
    }
    setConnectionStatus('disconnected');
    queryClient.removeQueries({ queryKey: ['research-session'] });
    queryClient.removeQueries({ queryKey: ['research-report'] });
  };

  return {
    // Session management
    sessionId,
    sessionData,
    sessionError,
    sessionLoading,
    
    // Real-time updates
    realTimeProgress,
    connectionStatus,
    
    // Report data
    reportData,
    
    // Actions
    startResearch: startResearchMutation.mutate,
    isStarting: startResearchMutation.isPending,
    startError: startResearchMutation.error,
    resetSession,
    
    // Combined state
    currentState: {
      stage: realTimeProgress?.stage || sessionData?.stage || 'idle',
      progress: realTimeProgress?.progress || sessionData?.progress || 0,
      language: sessionData?.language || 'en',
      research_question: sessionData?.research_question || '',
      final_report: reportData?.report || sessionData?.final_report,
      error: realTimeProgress?.error || sessionError?.message,
    },
  };
}