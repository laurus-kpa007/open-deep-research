"""Research state models based on original Open Deep Research implementation."""

from typing import List, Optional, Literal, Dict, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState, add_messages
import uuid
from datetime import datetime

LanguageCode = Literal["ko", "en"]

class ConductResearch(BaseModel):
    """Research task specification for individual researchers."""
    research_question: str = Field(description="Specific research question to investigate")
    description: str = Field(description="Detailed description of research scope and expectations")

class Summary(BaseModel):
    """Research summary with key excerpts and citations."""
    research_question: str = Field(description="Original research question")
    summary: str = Field(description="Comprehensive summary of findings")
    key_excerpts: List[str] = Field(default_factory=list, description="Important quotes and excerpts")
    sources: List[str] = Field(default_factory=list, description="List of source URLs")

class ResearchQuestion(BaseModel):
    """Structured research question with guidance."""
    question: str = Field(description="The research question")
    guidance: str = Field(description="Guidance for conducting the research")

class ClarifyWithUser(BaseModel):
    """User clarification request model."""
    clarification_request: str = Field(description="What needs to be clarified with the user")

class ResearchState(TypedDict):
    """
    Main research state based on original AgentState from Open Deep Research.
    Uses TypedDict for LangGraph compatibility while maintaining type safety.
    """
    # Messages from LangGraph MessagesState
    messages: Annotated[list, add_messages]
    
    # Core research data
    research_question: str
    clarified_research_goal: Optional[str]
    research_brief: Optional[str]
    
    # Supervisor and researcher coordination
    supervisor_requests: Optional[List[Dict[str, Any]]]  # Will contain ConductResearch data
    research_summaries: List[Dict[str, Any]]  # Will contain Summary data
    
    # Final output
    final_report: Optional[str]
    
    # Session management
    session_id: str
    language: LanguageCode
    created_at: Optional[datetime]
    last_updated: Optional[datetime]
    
    # Progress tracking
    current_stage: str
    progress: int
    
    # Configuration
    max_researchers: int
    max_iterations: int

# Helper functions for ResearchState
def create_research_state(
    research_question: str,
    language: LanguageCode = "en",
    max_researchers: int = 5
) -> ResearchState:
    """Create a new ResearchState with default values."""
    return ResearchState(
        messages=[],
        research_question=research_question,
        clarified_research_goal=None,
        research_brief=None,
        supervisor_requests=None,
        research_summaries=[],
        final_report=None,
        session_id=str(uuid.uuid4()),
        language=language,
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        current_stage="initializing",
        progress=0,
        max_researchers=max_researchers,
        max_iterations=6
    )

def update_research_progress(state: ResearchState, stage: str, progress: int) -> None:
    """Update research state progress."""
    state["current_stage"] = stage
    state["progress"] = progress
    state["last_updated"] = datetime.utcnow()

class ResearchRequest(BaseModel):
    """Request model for starting research."""
    query: str = Field(description="Research question or topic")
    language: Optional[LanguageCode] = Field(default=None, description="Preferred language (auto-detect if None)")
    depth: Literal["shallow", "medium", "deep"] = Field(default="deep", description="Research depth")
    max_researchers: int = Field(default=5, description="Maximum parallel researchers")

class ResearchResponse(BaseModel):
    """Response model for research requests."""
    session_id: str
    status: str
    language: LanguageCode
    message: str

class ResearchProgress(BaseModel):
    """Progress update model for WebSocket communication."""
    session_id: str
    stage: str
    progress: int
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None