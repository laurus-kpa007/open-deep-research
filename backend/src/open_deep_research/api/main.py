"""Main FastAPI application for Deep Research Agent."""

import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
from datetime import datetime
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socketio
from dotenv import load_dotenv

from ..models.state import (
    ResearchRequest, ResearchResponse, ResearchProgress,
    ResearchState, LanguageCode, create_research_state, DetailedProgress
)
from ..core.llm_adapter import get_llm_client
from ..core.llm_providers import BaseLLMClient
from ..core.research_workflow import ResearchWorkflow
from ..services.search_service import SearchService
from ..services.session_manager import SessionManager
from ..utils.language_detector import LanguageDetector

# Load environment variables from root directory
from pathlib import Path
root_dir = Path(__file__).resolve().parents[4]  # Navigate to project root
env_path = root_dir / '.env'
load_dotenv(env_path)

# Import CORS configuration
import sys
sys.path.insert(0, str(root_dir))
from cors_config import get_cors_config, get_cors_origins

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Global instances
llm_client: BaseLLMClient = None
search_service: SearchService = None
research_workflow: ResearchWorkflow = None
session_manager: SessionManager = None
active_sessions: Dict[str, ResearchState] = {}
websocket_connections: Dict[str, WebSocket] = {}

# Socket.IO server for real-time communication
# Socket.IO needs "*" for development or explicit origins
cors_origins = get_cors_origins()
logger.info(f"Socket.IO CORS origins: {cors_origins}")

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*" if os.getenv("ENVIRONMENT", "development") == "development" else cors_origins
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global llm_client, search_service, research_workflow, session_manager

    logger.info("Initializing Deep Research Agent...")

    # Initialize services
    try:
        # Initialize LLM client based on provider configuration
        provider = os.getenv("LLM_PROVIDER", "ollama")
        logger.info(f"Initializing LLM client with provider: {provider}")
        llm_client = get_llm_client(provider=provider)
        logger.info(f"{provider.upper()} client initialized")

        # Check LLM health
        if not await llm_client.health_check():
            logger.warning(f"{provider.upper()} server not available, attempting to continue...")
            # In production, you might want to wait or fail here
        
        # Initialize search service
        search_service = SearchService()
        if await search_service.health_check():
            logger.info("Search service initialized successfully")
        else:
            logger.warning("Search service not available")
        
        # Initialize research workflow
        research_workflow = ResearchWorkflow(llm_client, search_service)
        logger.info("Research workflow initialized")
        
        # Initialize session manager
        session_manager = SessionManager()
        logger.info("Session manager initialized")
        
        # Load existing sessions
        existing_sessions = await session_manager.list_sessions()
        logger.info(f"Found {len(existing_sessions)} existing sessions")
        
        logger.info("Deep Research Agent started successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down Deep Research Agent...")

# Create FastAPI app
app = FastAPI(
    title="Deep Research Agent API",
    description="Web-based implementation of Open Deep Research Agent with Ollama",
    version="0.1.0",
    lifespan=lifespan
)

# Add CORS middleware with proper configuration
cors_config = get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
    expose_headers=cors_config["expose_headers"]
)

# Mount Socket.IO
socket_app = socketio.ASGIApp(sio, app)

class WebSocketManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Connect a WebSocket for a session."""
        await websocket.accept()
        self.connections[session_id] = websocket
        logger.info(f"WebSocket connected for session: {session_id}")
    
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket."""
        if session_id in self.connections:
            del self.connections[session_id]
            logger.info(f"WebSocket disconnected for session: {session_id}")
    
    async def send_progress(self, session_id: str, progress_data: Dict[str, Any]):
        """Send progress update to WebSocket."""
        if session_id not in self.connections:
            logger.debug(f"No WebSocket connection for session {session_id}")
            return
            
        try:
            websocket = self.connections[session_id]
            await websocket.send_json(progress_data)
        except Exception as e:
            logger.warning(f"Failed to send progress to {session_id}: {e}")
            self.disconnect(session_id)

websocket_manager = WebSocketManager()

# Progress callback for research workflow
async def progress_callback(session_id: str, stage: str, progress: int, data: Dict[str, Any] = None):
    """Callback for research progress updates."""
    try:
        progress_data = {
            "type": "progress_update",
            "session_id": session_id,
            "stage": stage,
            "progress": progress,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add detailed progress if available
        if data and "detailed" in data:
            progress_data["detailed"] = data["detailed"]
            
            # Also update the session state for API access
            if session_id in active_sessions:
                state = active_sessions[session_id]
                detailed_data = data.get("detailed", {})
                if "current_search_results" in detailed_data:
                    state["current_search_results"] = detailed_data["current_search_results"]
                if "preview" in detailed_data:
                    state["draft_content"] = detailed_data["preview"]
                
                # Save progress to persistent storage periodically
                if progress % 10 == 0:  # Save every 10% progress
                    asyncio.create_task(session_manager.update_session_progress(
                        session_id, stage, progress,
                        current_search_results=state.get("current_search_results", []),
                        draft_content=state.get("draft_content", "")
                    ))
        
        await websocket_manager.send_progress(session_id, progress_data)
        
        # Also emit via Socket.IO with more granular events
        if sio:
            await sio.emit("progress_update", progress_data, room=session_id)
            
            # Emit specific events for different progress types
            if data and "detailed" in data:
                detailed_data = data.get("detailed", {})
                detail_type = detailed_data.get("type")
                if detail_type:
                    await sio.emit(f"progress_{detail_type}", detailed_data, room=session_id)
    except Exception as e:
        logger.error(f"Error sending progress callback for session {session_id}: {e}")

# API Routes

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    provider = os.getenv("LLM_PROVIDER", "ollama")
    health_status = {
        "status": "healthy",
        "llm_provider": provider,
        "llm_available": False,
        "search_available": False,
        # Keep backward compatibility
        "ollama_available": False
    }

    try:
        if llm_client:
            llm_available = await llm_client.health_check()
            health_status["llm_available"] = llm_available
            health_status[f"{provider}_available"] = llm_available
            # For backward compatibility
            if provider == "ollama":
                health_status["ollama_available"] = llm_available

        if search_service:
            health_status["search_available"] = await search_service.health_check()
            
    except Exception as e:
        logger.error(f"Health check error: {e}")
    
    return health_status

@app.post("/api/v1/research/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """Start a new research session."""
    try:
        # Detect language if not specified
        language = request.language
        if not language:
            language = LanguageDetector.detect_language(request.query)
        
        # Create initial research state
        initial_state = create_research_state(
            research_question=request.query,
            language=language,
            max_researchers=request.max_researchers
        )
        
        # Store session
        session_id = initial_state["session_id"]
        active_sessions[session_id] = initial_state
        
        # Save to persistent storage
        await session_manager.save_session(session_id, initial_state)
        
        # Start research in background
        background_tasks.add_task(
            execute_research_workflow,
            session_id,
            initial_state
        )
        
        return ResearchResponse(
            session_id=session_id,
            status="started",
            language=language,
            message="Research started successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to start research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_research_workflow(session_id: str, initial_state: ResearchState):
    """Execute the research workflow in background."""
    try:
        logger.info(f"Starting research workflow for session: {session_id}")
        logger.info(f"Initial state type: {type(initial_state)}")
        logger.info(f"Initial state has session_id: {'session_id' in initial_state if isinstance(initial_state, dict) else 'Not a dict'}")
        
        # Send initial progress
        await progress_callback(session_id, "initializing", 5)
        
        # Create a lambda wrapper for progress_callback to include session_id
        async def workflow_progress_callback(stage: str, progress: int, data: Dict[str, Any] = None):
            try:
                await progress_callback(session_id, stage, progress, data)
            except Exception as e:
                logger.warning(f"Progress callback error for session {session_id}: {e}")
        
        # Run workflow with wrapped callback
        final_state = await research_workflow.run_research(initial_state, workflow_progress_callback)
        
        # Update stored session
        active_sessions[session_id] = final_state
        
        # Save final state to persistent storage
        await session_manager.save_session(session_id, final_state)
        
        # Send completion
        if isinstance(final_state, dict):
            await progress_callback(
                session_id,
                final_state.get("current_stage", "completed"),
                final_state.get("progress", 100),
                {"final_report": final_state.get("final_report")}
            )
        else:
            logger.error(f"Final state is not a dict: {type(final_state)}")
        
        logger.info(f"Research workflow completed for session: {session_id}")
        
    except Exception as e:
        logger.error(f"Research workflow failed for session {session_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        await progress_callback(
            session_id,
            "error",
            0,
            {"error": str(e)}
        )

@app.get("/api/v1/research/{session_id}")
async def get_research_status(session_id: str):
    """Get current research session status."""
    # Try to get from memory first
    state = active_sessions.get(session_id)
    
    # If not in memory, try to load from storage
    if not state:
        state = await session_manager.load_session(session_id)
        if state:
            active_sessions[session_id] = state
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    # Update the reference
    state = active_sessions[session_id]
    
    return {
        "session_id": session_id,
        "stage": state["current_stage"],
        "progress": state["progress"],
        "language": state["language"],
        "research_question": state["research_question"],
        "final_report": state["final_report"],
        "detailed_progress": state.get("detailed_progress", [])[-10:],  # Last 10 updates
        "current_search_results": state.get("current_search_results", []),
        "current_thoughts": state.get("current_thoughts", ""),
        "draft_content": (state.get("draft_content") or "")[-1000:],  # Last 1000 chars
        "research_tasks": [
            {"question": t.get("research_question"), "completed": i < len(state.get("research_summaries", []))}
            for i, t in enumerate(state.get("supervisor_requests", []))
        ] if state.get("supervisor_requests") else [],
        "created_at": state["created_at"].isoformat() if state["created_at"] else None,
        "last_updated": state["last_updated"].isoformat() if state["last_updated"] else None
    }

@app.get("/api/v1/research")
async def list_research_sessions():
    """List all research sessions."""
    try:
        sessions = await session_manager.list_sessions()
        return {
            "sessions": sessions,
            "total": len(sessions)
        }
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return {"sessions": [], "total": 0}

@app.delete("/api/v1/research/{session_id}")
async def delete_research_session(session_id: str):
    """Delete a research session."""
    try:
        # Remove from memory
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        # Remove from storage
        success = await session_manager.delete_session(session_id)
        
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/research/{session_id}/report")
async def get_research_report(session_id: str):
    """Get the final research report."""
    # Try to get from memory first
    state = active_sessions.get(session_id)
    
    # If not in memory, try to load from storage
    if not state:
        state = await session_manager.load_session(session_id)
        if state:
            active_sessions[session_id] = state
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    
    # Update the reference
    state = active_sessions[session_id]
    
    if not state["final_report"]:
        raise HTTPException(status_code=404, detail="Report not yet available")
    
    return {
        "session_id": session_id,
        "report": state["final_report"],
        "language": state["language"],
        "research_question": state["research_question"],
        "sources": [s.get("sources", []) for s in state["research_summaries"]] if state["research_summaries"] else [],
        "generated_at": state["last_updated"].isoformat() if state["last_updated"] else None
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await websocket_manager.connect(session_id, websocket)
    
    try:
        # Send current status if session exists
        if session_id in active_sessions:
            state = active_sessions[session_id]
            await websocket.send_json({
                "type": "status_update",
                "session_id": session_id,
                "stage": state["current_stage"],
                "progress": state["progress"],
                "detailed_progress": state.get("detailed_progress", [])[-5:],
                "current_search_results": state.get("current_search_results", []),
                "draft_content": state.get("draft_content", "")[-500:]
            })
        
        # Keep connection alive
        while True:
            try:
                data = await websocket.receive_text()
                # Handle any client messages if needed
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        websocket_manager.disconnect(session_id)

# Socket.IO events
@sio.event
async def connect(sid, environ):
    """Socket.IO client connected."""
    logger.info(f"Socket.IO client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Socket.IO client disconnected."""
    logger.info(f"Socket.IO client disconnected: {sid}")

@sio.event
async def join_session(sid, data):
    """Join a research session room."""
    session_id = data.get("session_id")
    if session_id:
        await sio.enter_room(sid, session_id)
        logger.info(f"Client {sid} joined session {session_id}")

if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",  # Use the Socket.IO app
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )