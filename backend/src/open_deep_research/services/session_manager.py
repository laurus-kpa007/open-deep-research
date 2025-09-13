"""Session management with file-based persistence."""

import json
import os
import pickle
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
import aiofiles
import asyncio

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages research sessions with file-based persistence."""
    
    def __init__(self, storage_dir: str = None):
        """Initialize session manager with storage directory."""
        self.storage_dir = Path(storage_dir or os.getenv("SESSION_STORAGE_DIR", "./sessions"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_cache: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        logger.info(f"Session storage initialized at: {self.storage_dir}")
    
    async def save_session(self, session_id: str, state: Dict[str, Any]) -> bool:
        """Save session state to disk."""
        try:
            async with self._lock:
                # Convert datetime objects to ISO format for JSON serialization
                serializable_state = self._make_serializable(state.copy())
                
                session_file = self.storage_dir / f"{session_id}.json"
                async with aiofiles.open(session_file, 'w') as f:
                    await f.write(json.dumps(serializable_state, indent=2))
                
                # Update cache
                self.sessions_cache[session_id] = state
                logger.info(f"Session {session_id} saved successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            return False
    
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session state from disk."""
        try:
            # Check cache first
            if session_id in self.sessions_cache:
                return self.sessions_cache[session_id]
            
            session_file = self.storage_dir / f"{session_id}.json"
            if not session_file.exists():
                logger.debug(f"Session file not found: {session_id}")
                return None
            
            async with aiofiles.open(session_file, 'r') as f:
                content = await f.read()
                state = json.loads(content)
                
            # Convert ISO strings back to datetime objects
            state = self._restore_datetimes(state)
            
            # Update cache
            self.sessions_cache[session_id] = state
            logger.info(f"Session {session_id} loaded from disk")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session from storage."""
        try:
            async with self._lock:
                session_file = self.storage_dir / f"{session_id}.json"
                if session_file.exists():
                    session_file.unlink()
                
                if session_id in self.sessions_cache:
                    del self.sessions_cache[session_id]
                
                logger.info(f"Session {session_id} deleted")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def list_sessions(self) -> list:
        """List all available sessions."""
        try:
            sessions = []
            for session_file in self.storage_dir.glob("*.json"):
                session_id = session_file.stem
                
                # Try to load basic info without full state
                try:
                    async with aiofiles.open(session_file, 'r') as f:
                        content = await f.read()
                        state = json.loads(content)
                        
                    sessions.append({
                        "session_id": session_id,
                        "created_at": state.get("created_at"),
                        "last_updated": state.get("last_updated"),
                        "current_stage": state.get("current_stage"),
                        "progress": state.get("progress", 0),
                        "research_question": state.get("research_question")
                    })
                except Exception as e:
                    logger.warning(f"Failed to read session {session_id}: {e}")
                    
            return sorted(sessions, key=lambda x: x.get("last_updated", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []
    
    async def cleanup_old_sessions(self, days: int = 7) -> int:
        """Clean up sessions older than specified days."""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = 0
            
            for session_file in self.storage_dir.glob("*.json"):
                try:
                    async with aiofiles.open(session_file, 'r') as f:
                        content = await f.read()
                        state = json.loads(content)
                    
                    last_updated = state.get("last_updated")
                    if last_updated:
                        last_updated_dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                        if last_updated_dt < cutoff_date:
                            session_file.unlink()
                            deleted_count += 1
                            logger.info(f"Deleted old session: {session_file.stem}")
                            
                except Exception as e:
                    logger.warning(f"Failed to process session file {session_file}: {e}")
            
            logger.info(f"Cleaned up {deleted_count} old sessions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
    
    def _make_serializable(self, obj: Any) -> Any:
        """Convert non-serializable objects to JSON-serializable format."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return self._make_serializable(obj.__dict__)
        else:
            return obj
    
    def _restore_datetimes(self, obj: Any) -> Any:
        """Restore datetime objects from ISO format strings."""
        if isinstance(obj, str):
            # Try to parse as datetime
            try:
                if 'T' in obj and len(obj) >= 19:  # Basic ISO format check
                    return datetime.fromisoformat(obj.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass
            return obj
        elif isinstance(obj, dict):
            # Special handling for known datetime fields
            datetime_fields = ['created_at', 'last_updated', 'timestamp']
            result = {}
            for k, v in obj.items():
                if k in datetime_fields and isinstance(v, str):
                    try:
                        result[k] = datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        result[k] = v
                else:
                    result[k] = self._restore_datetimes(v)
            return result
        elif isinstance(obj, list):
            return [self._restore_datetimes(item) for item in obj]
        else:
            return obj
    
    async def update_session_progress(
        self, 
        session_id: str, 
        stage: str, 
        progress: int,
        **kwargs
    ) -> bool:
        """Update session progress and save."""
        try:
            state = await self.load_session(session_id)
            if not state:
                logger.warning(f"Session {session_id} not found for progress update")
                return False
            
            state["current_stage"] = stage
            state["progress"] = progress
            state["last_updated"] = datetime.utcnow()
            
            # Update additional fields if provided
            for key, value in kwargs.items():
                state[key] = value
            
            return await self.save_session(session_id, state)
            
        except Exception as e:
            logger.error(f"Failed to update session progress {session_id}: {e}")
            return False