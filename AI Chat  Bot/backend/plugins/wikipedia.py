"""
Wikipedia plugin for the AI Chatbot.
Provides information from Wikipedia articles and searches.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from .base import BasePlugin, PluginResponse


class WikipediaPlugin(BasePlugin):
    """Plugin for getting Wikipedia information."""
    
    def __init__(self):
        super().__init__(
            name="wikipedia",
            description="Search and retrieve information from Wikipedia",
            version="1.0.0"
        )
        self.required_api_keys = []  # Wikipedia API is free
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
    
    def get_capabilities(self) -> list[str]:
        return [
            "article_search",
            "article_summary",
            "article_content",
            "random_article",
            "related_articles"
        ]
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        # At least one of these parameters should be provided
        valid_params = ["query", "title", "page_id"]
        return any(param in kwargs for param in valid_params)
    
    async def execute(self, **kwargs) -> PluginResponse:
        """Execute the Wikipedia plugin."""
        try:
            # Determine the type of request
            if "query" in kwargs:
                # Search for articles
                search_results = await self._search_articles(kwargs["query"])
                if not search_results:
                    return PluginResponse(
                        success=False,
                        error=f"No Wikipedia articles found for '{kwargs['query']}'"
                    )
                
                return PluginResponse(
                    success=True,
                    data=search_results,
                    metadata={
                        "query": kwargs["query"],
                        "total_results": len(search_results.get("results", [])),
                        "source": "Wikipedia"
                    }
                )
            
            elif "title" in kwargs:
                # Get article summary by title
                article_data = await self._get_article_summary(kwargs["title"])
                if not article_data:
                    return PluginResponse(
                        success=False,
                        error=f"Could not retrieve Wikipedia article for '{kwargs['title']}'"
                    )
                
                return PluginResponse(
                    success=True,
                    data=article_data,
                    metadata={
                        "title": kwargs["title"],
                        "source": "Wikipedia"
                    }
                )
            
            elif "page_id" in kwargs:
                # Get article by page ID
                article_data = await self._get_article_by_id(kwargs["page_id"])
                if not article_data:
                    return PluginResponse(
                        success=False,
                        error=f"Could not retrieve Wikipedia article with ID {kwargs['page_id']}"
                    )
                
                return PluginResponse(
                    success=True,
                    data=article_data,
                    metadata={
                        "page_id": kwargs["page_id"],
                        "source": "Wikipedia"
                    }
                )
            
            else:
                return PluginResponse(
                    success=False,
                    error="No valid parameters provided. Use 'query', 'title', or 'page_id'"
                )
            
        except Exception as e:
            return PluginResponse(
                success=False,
                error=f"Wikipedia plugin error: {str(e)}"
            )
    
    async def _search_articles(self, query: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """Search for Wikipedia articles."""
        try:
            url = f"{self.base_url}/page/search/{query}"
            params = {"limit": limit}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_search_results(data)
                    else:
                        print(f"Wikipedia API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error searching Wikipedia articles: {e}")
            return None
    
    async def _get_article_summary(self, title: str) -> Optional[Dict[str, Any]]:
        """Get a Wikipedia article summary by title."""
        try:
            # First, search for the exact title
            search_results = await self._search_articles(title, limit=1)
            if not search_results or not search_results.get("results"):
                return None
            
            # Get the first result
            first_result = search_results["results"][0]
            page_id = first_result.get("id")
            
            if page_id:
                return await self._get_article_by_id(page_id)
            
            return None
            
        except Exception as e:
            print(f"Error getting article summary: {e}")
            return None
    
    async def _get_article_by_id(self, page_id: int) -> Optional[Dict[str, Any]]:
        """Get a Wikipedia article by page ID."""
        try:
            url = f"{self.base_url}/page/summary/{page_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_article_data(data)
                    else:
                        print(f"Wikipedia API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error getting article by ID: {page_id}")
            return None
    
    def _format_search_results(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Wikipedia search results."""
        try:
            pages = search_data.get("pages", [])
            formatted_results = []
            
            for page in pages:
                formatted_result = {
                    "id": page.get("id"),
                    "title": page.get("title", "No title"),
                    "description": page.get("description", "No description"),
                    "url": page.get("url", ""),
                    "thumbnail": page.get("thumbnail", {}).get("url", ""),
                    "extract": page.get("extract", ""),
                    "page_id": page.get("pageid")
                }
                formatted_results.append(formatted_result)
            
            return {
                "query": search_data.get("query", ""),
                "total_results": len(formatted_results),
                "results": formatted_results
            }
            
        except Exception as e:
            print(f"Error formatting search results: {e}")
            return {"error": "Failed to format search results"}
    
    def _format_article_data(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format Wikipedia article data."""
        try:
            return {
                "id": article_data.get("id"),
                "title": article_data.get("title", "No title"),
                "description": article_data.get("description", "No description"),
                "extract": article_data.get("extract", "No content available"),
                "url": article_data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                "thumbnail": article_data.get("thumbnail", {}).get("url", ""),
                "coordinates": article_data.get("coordinates", {}),
                "page_id": article_data.get("pageid"),
                "language": article_data.get("lang", "en"),
                "timestamp": article_data.get("timestamp")
            }
            
        except Exception as e:
            print(f"Error formatting article data: {e}")
            return {"error": "Failed to format article data"}
    
    async def get_random_article(self) -> Optional[Dict[str, Any]]:
        """Get a random Wikipedia article."""
        try:
            url = f"{self.base_url}/page/random/summary"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_article_data(data)
                    else:
                        print(f"Wikipedia API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error getting random article: {e}")
            return None
    
    def get_usage_examples(self) -> list[str]:
        return [
            "Search for articles: wikipedia(query='artificial intelligence')",
            "Get article by title: wikipedia(title='Python programming language')",
            "Get article by ID: wikipedia(page_id=12345)"
        ]
    
    async def health_check(self) -> bool:
        """Check if the Wikipedia plugin is healthy."""
        try:
            # Try to get a random article to verify connectivity
            test_data = await self.get_random_article()
            return test_data is not None and "error" not in test_data
            
        except Exception:
            return False
