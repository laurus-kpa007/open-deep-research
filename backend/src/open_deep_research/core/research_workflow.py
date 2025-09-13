"""LangGraph-based research workflow implementation."""

import json
import logging
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from ..models.state import (
    ResearchState, ConductResearch, Summary, ClarifyWithUser,
    LanguageCode, update_research_progress, DetailedProgress
)
from ..prompts.multilingual_prompts import MultilingualPrompts
from ..core.ollama_client import OllamaClient
from ..services.search_service import SearchService
from ..utils.language_detector import LanguageDetector

logger = logging.getLogger(__name__)

class ResearchWorkflow:
    """LangGraph-based research workflow implementing the Open Deep Research pattern."""
    
    def __init__(self, ollama_client: OllamaClient, search_service: SearchService):
        self.ollama_client = ollama_client
        self.search_service = search_service
        self.language_detector = LanguageDetector()
        self.progress_callback = None
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow based on original Open Deep Research."""
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("clarify_with_user", self.clarify_with_user_node)
        workflow.add_node("write_research_brief", self.write_research_brief_node)
        workflow.add_node("research_supervisor", self.research_supervisor_node)
        workflow.add_node("research_individual", self.research_individual_node)
        workflow.add_node("compress_research", self.compress_research_node)
        workflow.add_node("final_report_generation", self.final_report_generation_node)
        
        # Set entry point
        workflow.set_entry_point("clarify_with_user")
        
        # Add edges
        workflow.add_edge("clarify_with_user", "write_research_brief")
        workflow.add_edge("write_research_brief", "research_supervisor")
        workflow.add_conditional_edges(
            "research_supervisor",
            self.should_continue_research,
            {
                "continue": "research_individual",
                "finalize": "compress_research"
            }
        )
        workflow.add_edge("research_individual", "research_supervisor")
        workflow.add_edge("compress_research", "final_report_generation")
        workflow.add_edge("final_report_generation", END)
        
        return workflow
    
    async def clarify_with_user_node(self, state: ResearchState) -> Dict[str, Any]:
        """Clarify research requirements with user."""
        try:
            update_research_progress(state, "clarifying", 10)
            
            # Send detailed progress if callback available
            if self.progress_callback:
                await self._send_detailed_progress(
                    state, "thinking", 
                    "연구 목표를 분석하고 있습니다...",
                    "사용자의 질문을 이해하고 연구 방향을 설정하는 중입니다."
                )
            
            # Send progress update if callback available
            if self.progress_callback:
                await self.progress_callback("clarifying", 10)
            
            # Detect language if not set
            if not state["language"] or state["language"] == "auto":
                state["language"] = self.language_detector.detect_language(state["research_question"])
            
            # Get clarification prompt
            prompt = MultilingualPrompts.get_prompt(
                "clarification",
                state["language"],
                research_question=state["research_question"]
            )
            
            # Generate clarification
            response = await self.ollama_client.generate(
                prompt, 
                stage="clarification"
            )
            
            # Check if we can proceed directly
            if "PROCEED_TO_RESEARCH" in response:
                clarified_goal = state["research_question"]
            else:
                # For now, use the original question as clarified goal
                # In a real implementation, this would involve user interaction
                clarified_goal = state["research_question"]
            
            return {
                "clarified_research_goal": clarified_goal,
                "current_stage": "clarified",
                "progress": 20,
                "messages": [AIMessage(content=response)]
            }
            
        except Exception as e:
            logger.error(f"Error in clarify_with_user_node: {e}")
            return {
                "current_stage": "error",
                "messages": [AIMessage(content=f"Error during clarification: {str(e)}")]
            }
    
    async def write_research_brief_node(self, state: ResearchState) -> Dict[str, Any]:
        """Generate comprehensive research brief."""
        try:
            update_research_progress(state, "briefing", 30)
            
            # Send detailed progress if callback available
            if self.progress_callback:
                await self._send_detailed_progress(
                    state, "writing",
                    "연구 계획서를 작성하고 있습니다...",
                    "연구 범위, 방법론, 예상 결과를 정의하는 중입니다."
                )
            
            # Send progress update if callback available
            if self.progress_callback:
                await self.progress_callback("briefing", 30)
            
            prompt = MultilingualPrompts.get_prompt(
                "research_brief",
                state["language"],
                clarified_research_goal=state["clarified_research_goal"]
            )
            
            research_brief = await self.ollama_client.generate(
                prompt,
                stage="brief"
            )
            
            return {
                "research_brief": research_brief,
                "current_stage": "brief_complete",
                "progress": 40,
                "messages": [AIMessage(content="Research brief generated successfully")]
            }
            
        except Exception as e:
            logger.error(f"Error in write_research_brief_node: {e}")
            return {
                "current_stage": "error",
                "messages": [AIMessage(content=f"Error writing research brief: {str(e)}")]
            }
    
    async def research_supervisor_node(self, state: ResearchState) -> Dict[str, Any]:
        """Supervise and coordinate research tasks."""
        try:
            # If we don't have research requests yet, generate them
            if not state["supervisor_requests"]:
                update_research_progress(state, "planning", 45)
                
                # Send progress update if callback available
                if self.progress_callback:
                    await self.progress_callback("planning", 45)
                
                prompt = MultilingualPrompts.get_prompt(
                    "supervisor",
                    state["language"],
                    research_brief=state["research_brief"]
                )
                
                response = await self.ollama_client.generate(
                    prompt,
                    stage="supervisor"
                )
                
                # Parse JSON response
                try:
                    # Extract JSON from response
                    json_start = response.find('[')
                    json_end = response.rfind(']') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = response[json_start:json_end]
                        tasks_data = json.loads(json_str)
                        
                        supervisor_requests = [
                            ConductResearch(**task) for task in tasks_data
                        ]
                    else:
                        # Fallback: create a single research task
                        supervisor_requests = [
                            ConductResearch(
                                research_question=state["clarified_research_goal"],
                                description="Comprehensive research on the given topic"
                            )
                        ]
                except (json.JSONDecodeError, KeyError):
                    logger.warning("Failed to parse supervisor response, using fallback")
                    supervisor_requests = [
                        ConductResearch(
                            research_question=state["clarified_research_goal"],
                            description="Comprehensive research on the given topic"
                        )
                    ]
                
                return {
                    "supervisor_requests": supervisor_requests,
                    "current_stage": "research_planned",
                    "progress": 50,
                    "messages": [AIMessage(content=f"Generated {len(supervisor_requests)} research tasks")]
                }
            
            # Check if we have enough research summaries
            if len(state["research_summaries"]) >= len(state["supervisor_requests"]):
                return {
                    "current_stage": "research_complete",
                    "progress": 80,
                    "messages": [AIMessage(content="All research tasks completed")]
                }
            
            return {
                "current_stage": "coordinating",
                "messages": [AIMessage(content="Coordinating research tasks")]
            }
            
        except Exception as e:
            logger.error(f"Error in research_supervisor_node: {e}")
            return {
                "current_stage": "error",
                "messages": [AIMessage(content=f"Error in supervision: {str(e)}")]
            }
    
    async def research_individual_node(self, state: ResearchState) -> Dict[str, Any]:
        """Conduct individual research tasks."""
        try:
            if not state["supervisor_requests"]:
                return {"messages": [AIMessage(content="No research tasks assigned")]}
            
            # Find next task to research
            completed_count = len(state["research_summaries"])
            if completed_count >= len(state["supervisor_requests"]):
                return {"messages": [AIMessage(content="All research tasks completed")]}
            
            current_task = state["supervisor_requests"][completed_count]
            progress = 50 + (completed_count / len(state["supervisor_requests"])) * 25
            update_research_progress(state, "researching", int(progress))
            
            # Send progress update if callback available
            if self.progress_callback:
                await self.progress_callback("researching", int(progress))
            
            # Send search start notification if callback available
            search_query = current_task["research_question"] if isinstance(current_task, dict) else current_task.research_question
            if self.progress_callback:
                await self._send_detailed_progress(
                    state, "searching",
                    f"웹 검색 중: {search_query[:50]}...",
                    f"Task {completed_count + 1}/{len(state['supervisor_requests'])}",
                    current_item=completed_count + 1,
                    total_items=len(state['supervisor_requests'])
                )
            
            # Conduct web search
            search_results = await self.search_service.search(
                search_query,
                max_results=10
            )
            
            # Update state with search results safely
            if "current_search_results" not in state:
                state["current_search_results"] = []
            state["current_search_results"] = search_results[:5]
            
            # Send search results notification if callback available
            if self.progress_callback:
                await self._send_detailed_progress(
                    state, "analyzing",
                    f"{len(search_results)}개의 검색 결과를 분석하고 있습니다...",
                    f"신뢰도 높은 소스를 선별하고 정보를 추출하는 중입니다.",
                    sources_found=len(search_results)
                )
            
            # Prepare research context
            search_context = "\n".join([
                f"Source: {result.get('title', 'Unknown')}\nURL: {result.get('url', 'Unknown')}\nContent: {result.get('content', '')[:1000]}...\n"
                for result in search_results[:5]
            ])
            
            # Generate research prompt
            research_q = current_task["research_question"] if isinstance(current_task, dict) else current_task.research_question
            task_desc = current_task["description"] if isinstance(current_task, dict) else current_task.description
            prompt = MultilingualPrompts.get_prompt(
                "researcher",
                state["language"],
                research_question=research_q,
                description=f"{task_desc}\n\nAvailable Information:\n{search_context}"
            )
            
            # Send LLM thinking notification if callback available
            if self.progress_callback:
                await self._send_detailed_progress(
                    state, "thinking",
                    "AI가 정보를 종합하여 연구를 수행하고 있습니다...",
                    f"수집된 자료를 바탕으로 심층 분석을 진행 중입니다.",
                    preview=search_context[:300] + "..."
                )
            
            # Store current thoughts safely
            if "current_thoughts" not in state:
                state["current_thoughts"] = ""
            state["current_thoughts"] = f"분석 중인 주제: {research_q}\n참고 자료: {len(search_results)}개"
            
            # Conduct research with streaming
            research_result = ""
            chunk_count = 0
            async for chunk in self.ollama_client.stream_generate(
                prompt,
                stage="research"
            ):
                research_result += chunk
                chunk_count += len(chunk)
                # Update draft content periodically
                if chunk_count >= 100:
                    chunk_count = 0
                    if "draft_content" not in state:
                        state["draft_content"] = ""
                    state["draft_content"] = research_result
                    if self.progress_callback:
                        await self._send_detailed_progress(
                            state, "writing",
                            "연구 내용을 작성하고 있습니다...",
                            preview=research_result[-500:] if len(research_result) > 500 else research_result
                        )
            
            # Create summary
            summary = {
                "research_question": research_q,
                "summary": research_result,
                "key_excerpts": [research_result[:500] + "..." if len(research_result) > 500 else research_result],
                "sources": [result.get('url', '') for result in search_results[:5]]
            }
            
            # Add to research summaries
            updated_summaries = list(state["research_summaries"]) + [summary]
            
            return {
                "research_summaries": updated_summaries,
                "current_stage": f"research_{completed_count + 1}_complete",
                "progress": int(progress),
                "messages": [AIMessage(content=f"Completed research task {completed_count + 1}/{len(state['supervisor_requests'])}")]
            }
            
        except Exception as e:
            logger.error(f"Error in research_individual_node: {e}")
            return {
                "current_stage": "error",
                "messages": [AIMessage(content=f"Error in individual research: {str(e)}")]
            }
    
    async def compress_research_node(self, state: ResearchState) -> Dict[str, Any]:
        """Compress and synthesize research findings."""
        try:
            update_research_progress(state, "synthesizing", 85)
            
            # Send detailed progress if callback available
            if self.progress_callback:
                await self._send_detailed_progress(
                    state, "synthesizing",
                    f"{len(state['research_summaries'])}개의 연구 결과를 통합하고 있습니다...",
                    "핵심 인사이트를 추출하고 일관된 내러티브를 구성하는 중입니다.",
                    current_item=len(state['research_summaries']),
                    total_items=len(state['research_summaries'])
                )
            
            # Send progress update if callback available
            if self.progress_callback:
                await self.progress_callback("synthesizing", 85)
            
            # Prepare research summaries text
            summaries_text = "\n\n---\n\n".join([
                f"Research Question: {summary.get('research_question', '')}\n"
                f"Summary: {summary.get('summary', '')}\n"
                f"Sources: {', '.join(summary.get('sources', []))}"
                for summary in state["research_summaries"]
            ])
            
            prompt = MultilingualPrompts.get_prompt(
                "compression",
                state["language"],
                research_summaries=summaries_text
            )
            
            compressed_research = await self.ollama_client.generate(
                prompt,
                stage="compression"
            )
            
            return {
                "final_report": compressed_research,
                "current_stage": "synthesis_complete",
                "progress": 90,
                "messages": [AIMessage(content="Research synthesis completed")]
            }
            
        except Exception as e:
            logger.error(f"Error in compress_research_node: {e}")
            return {
                "current_stage": "error",
                "messages": [AIMessage(content=f"Error in research compression: {str(e)}")]
            }
    
    async def final_report_generation_node(self, state: ResearchState) -> Dict[str, Any]:
        """Generate final polished report."""
        try:
            update_research_progress(state, "finalizing", 95)
            
            # Send detailed progress if callback available
            if self.progress_callback:
                await self._send_detailed_progress(
                    state, "formatting",
                    "최종 보고서를 정리하고 있습니다...",
                    "참고문헌, 인용구, 형식을 검토하는 중입니다.",
                    confidence=0.95
                )
            
            # Send progress update if callback available
            if self.progress_callback:
                await self.progress_callback("finalizing", 95)
            
            # The compressed research is already our final report
            # In a more complex implementation, this could do additional formatting
            
            return {
                "current_stage": "completed",
                "progress": 100,
                "messages": [AIMessage(content="Research completed successfully!")]
            }
            
        except Exception as e:
            logger.error(f"Error in final_report_generation_node: {e}")
            return {
                "current_stage": "error",
                "messages": [AIMessage(content=f"Error in final report generation: {str(e)}")]
            }
    
    def should_continue_research(self, state: ResearchState) -> str:
        """Determine if research should continue or finalize."""
        if not state["supervisor_requests"]:
            return "finalize"
        
        if len(state["research_summaries"]) >= len(state["supervisor_requests"]):
            return "finalize"
        
        return "continue"
    
    async def run_research(self, initial_state: ResearchState, progress_callback=None) -> ResearchState:
        """Run the complete research workflow."""
        try:
            # Set progress callback for workflow nodes
            self.progress_callback = progress_callback
            
            # Execute workflow
            final_state_dict = await self.app.ainvoke(initial_state)
            
            # Convert dict result back to ResearchState
            if isinstance(final_state_dict, dict):
                # Update initial_state with final results
                for key, value in final_state_dict.items():
                    if key in initial_state:
                        initial_state[key] = value
                return initial_state
            else:
                return final_state_dict
                
        except Exception as e:
            logger.error(f"Error running research workflow: {e}")
            # Return state with error
            initial_state["current_stage"] = "error"
            initial_state["progress"] = 0
            return initial_state
    
    async def _send_detailed_progress(
        self,
        state: ResearchState,
        progress_type: str,
        message: str,
        details: str = None,
        **kwargs
    ):
        """Send detailed progress update."""
        if not self.progress_callback:
            return
        
        try:
            detailed_progress = DetailedProgress(
                type=progress_type,
                message=message,
                details=details,
                **kwargs
            )
            
            # Convert to dict safely (use dict() for compatibility)
            try:
                progress_dict = detailed_progress.model_dump()
            except AttributeError:
                # Fallback for older pydantic versions
                progress_dict = detailed_progress.dict()
            
            # Add to state's detailed progress safely
            if "detailed_progress" not in state:
                state["detailed_progress"] = []
            state["detailed_progress"].append(progress_dict)
            
            # Send via callback
            await self.progress_callback(
                state["current_stage"],
                state["progress"],
                {"detailed": progress_dict}
            )
        except Exception as e:
            logger.warning(f"Error sending detailed progress: {e}")
    
