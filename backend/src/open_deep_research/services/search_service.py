"""Search service integration for web research."""

import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
import aiohttp
from tavily import TavilyClient

logger = logging.getLogger(__name__)

class SearchService:
    """Service for conducting web searches using Tavily API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            logger.warning("No Tavily API key provided. Search functionality will be limited.")
            self.client = None
        else:
            self.client = TavilyClient(api_key=self.api_key)
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "advanced",
        include_images: bool = False,
        include_answer: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform web search using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_depth: "basic" or "advanced"
            include_images: Whether to include images
            include_answer: Whether to include AI-generated answer
            
        Returns:
            List of search results with title, url, content, and score
        """
        if not self.client:
            logger.error("Tavily client not initialized. Check API key.")
            return []
        
        try:
            # Perform search using Tavily
            response = await asyncio.to_thread(
                self.client.search,
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_images=include_images,
                include_answer=include_answer
            )
            
            # Extract results
            results = []
            if 'results' in response:
                for item in response['results']:
                    result = {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'score': item.get('score', 0.0),
                        'published_date': item.get('published_date', ''),
                    }
                    results.append(result)
            
            # Add AI answer if available
            if include_answer and 'answer' in response:
                results.insert(0, {
                    'title': 'AI Summary',
                    'url': 'tavily://ai-answer',
                    'content': response['answer'],
                    'score': 1.0,
                    'type': 'ai_summary'
                })
            
            logger.info(f"Search completed for '{query}': {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    async def search_news(
        self,
        query: str,
        max_results: int = 5,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Search for recent news articles.
        
        Args:
            query: Search query
            max_results: Maximum results
            days: Number of days back to search
            
        Returns:
            List of news results
        """
        if not self.client:
            return []
        
        try:
            # Add time constraint to query
            time_query = f"{query} (recent news last {days} days)"
            
            response = await asyncio.to_thread(
                self.client.search,
                query=time_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["reuters.com", "bbc.com", "cnn.com", "ap.org"]
            )
            
            results = []
            if 'results' in response:
                for item in response['results']:
                    # Filter for recent content
                    result = {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'score': item.get('score', 0.0),
                        'published_date': item.get('published_date', ''),
                        'type': 'news'
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"News search failed for query '{query}': {e}")
            return []
    
    async def search_academic(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for academic content.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of academic results
        """
        if not self.client:
            return []
        
        try:
            # Focus on academic domains
            academic_query = f"{query} site:arxiv.org OR site:scholar.google.com OR site:pubmed.ncbi.nlm.nih.gov"
            
            response = await asyncio.to_thread(
                self.client.search,
                query=academic_query,
                search_depth="advanced",
                max_results=max_results
            )
            
            results = []
            if 'results' in response:
                for item in response['results']:
                    result = {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'content': item.get('content', ''),
                        'score': item.get('score', 0.0),
                        'published_date': item.get('published_date', ''),
                        'type': 'academic'
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Academic search failed for query '{query}': {e}")
            return []
    
    async def multi_source_search(
        self,
        query: str,
        max_results_per_source: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform searches across multiple source types.
        
        Args:
            query: Search query
            max_results_per_source: Max results per source type
            
        Returns:
            Dictionary with results categorized by source type
        """
        try:
            # Run all searches concurrently
            search_tasks = [
                self.search(query, max_results_per_source),
                self.search_news(query, max_results_per_source),
                self.search_academic(query, max_results_per_source)
            ]
            
            web_results, news_results, academic_results = await asyncio.gather(
                *search_tasks, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(web_results, Exception):
                logger.error(f"Web search failed: {web_results}")
                web_results = []
            if isinstance(news_results, Exception):
                logger.error(f"News search failed: {news_results}")
                news_results = []
            if isinstance(academic_results, Exception):
                logger.error(f"Academic search failed: {academic_results}")
                academic_results = []
            
            return {
                'web': web_results,
                'news': news_results,
                'academic': academic_results
            }
            
        except Exception as e:
            logger.error(f"Multi-source search failed: {e}")
            return {'web': [], 'news': [], 'academic': []}
    
    async def health_check(self) -> bool:
        """Check if the search service is available."""
        if not self.client:
            return False
        
        try:
            # Try a simple search
            response = await asyncio.to_thread(
                self.client.search,
                query="test",
                max_results=1
            )
            return bool(response)
        except Exception as e:
            logger.error(f"Search service health check failed: {e}")
            return False