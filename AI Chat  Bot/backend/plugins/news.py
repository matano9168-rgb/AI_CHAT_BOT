"""
News plugin for the AI Chatbot.
Provides current news information from various sources.
"""

import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from .base import BasePlugin, PluginResponse


class NewsPlugin(BasePlugin):
    """Plugin for getting news information."""
    
    def __init__(self):
        super().__init__(
            name="news",
            description="Get current news from various sources and categories",
            version="1.0.0"
        )
        self.required_api_keys = ["news_api_key"]
        self.base_url = "https://newsapi.org/v2"
    
    def get_capabilities(self) -> list[str]:
        return [
            "top_headlines",
            "news_by_category",
            "news_by_source",
            "news_search",
            "news_by_country"
        ]
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters."""
        # At least one of these parameters should be provided
        valid_params = ["category", "source", "query", "country"]
        return any(param in kwargs for param in valid_params)
    
    async def execute(self, **kwargs) -> PluginResponse:
        """Execute the news plugin."""
        try:
            api_key = self.api_keys.get("news_api_key")
            if not api_key:
                return PluginResponse(
                    success=False,
                    error="News API key not configured"
                )
            
            # Determine the type of news request
            if "category" in kwargs:
                news_data = await self._get_top_headlines(
                    category=kwargs["category"],
                    country=kwargs.get("country", "us"),
                    page_size=kwargs.get("page_size", 10)
                )
            elif "source" in kwargs:
                news_data = await self._get_news_by_source(
                    source=kwargs["source"],
                    page_size=kwargs.get("page_size", 10)
                )
            elif "query" in kwargs:
                news_data = await self._get_news_search(
                    query=kwargs["query"],
                    page_size=kwargs.get("page_size", 10)
                )
            else:
                # Default to top headlines
                news_data = await self._get_top_headlines(
                    country=kwargs.get("country", "us"),
                    page_size=kwargs.get("page_size", 10)
                )
            
            if not news_data:
                return PluginResponse(
                    success=False,
                    error="Could not retrieve news data"
                )
            
            # Format the response
            formatted_response = self._format_news_response(news_data)
            
            return PluginResponse(
                success=True,
                data=formatted_response,
                metadata={
                    "total_results": news_data.get("totalResults", 0),
                    "request_type": self._get_request_type(kwargs),
                    "source": "NewsAPI"
                }
            )
            
        except Exception as e:
            return PluginResponse(
                success=False,
                error=f"News plugin error: {str(e)}"
            )
    
    async def _get_top_headlines(self, category: str = None, country: str = "us", 
                                page_size: int = 10) -> Optional[Dict[str, Any]]:
        """Get top headlines by category and country."""
        try:
            url = f"{self.base_url}/top-headlines"
            params = {
                "apiKey": self.api_keys["news_api_key"],
                "country": country,
                "pageSize": page_size
            }
            
            if category:
                params["category"] = category
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"News API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error fetching top headlines: {e}")
            return None
    
    async def _get_news_by_source(self, source: str, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """Get news from a specific source."""
        try:
            url = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_keys["news_api_key"],
                "sources": source,
                "pageSize": page_size,
                "sortBy": "publishedAt"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"News API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error fetching news by source: {e}")
            return None
    
    async def _get_news_search(self, query: str, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """Search for news articles."""
        try:
            url = f"{self.base_url}/everything"
            params = {
                "apiKey": self.api_keys["news_api_key"],
                "q": query,
                "pageSize": page_size,
                "sortBy": "relevancy"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"News API error: {response.status}")
                        return None
                        
        except Exception as e:
            print(f"Error fetching news search: {e}")
            return None
    
    def _format_news_response(self, news_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format news data into a user-friendly response."""
        try:
            articles = news_data.get("articles", [])
            formatted_articles = []
            
            for article in articles:
                formatted_article = {
                    "title": article.get("title", "No title"),
                    "description": article.get("description", "No description"),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author", "Unknown"),
                    "published_at": article.get("publishedAt", ""),
                    "content": article.get("content", "")
                }
                formatted_articles.append(formatted_article)
            
            return {
                "total_results": news_data.get("totalResults", 0),
                "articles": formatted_articles,
                "status": news_data.get("status", "unknown")
            }
            
        except Exception as e:
            print(f"Error formatting news response: {e}")
            return {"error": "Failed to format news data"}
    
    def _get_request_type(self, kwargs: Dict[str, Any]) -> str:
        """Determine the type of news request."""
        if "category" in kwargs:
            return "top_headlines_by_category"
        elif "source" in kwargs:
            return "news_by_source"
        elif "query" in kwargs:
            return "news_search"
        else:
            return "top_headlines"
    
    def get_usage_examples(self) -> list[str]:
        return [
            "Get top headlines: news(country='us')",
            "Get business news: news(category='business', country='us')",
            "Get news from BBC: news(source='bbc-news')",
            "Search for AI news: news(query='artificial intelligence')"
        ]
    
    async def health_check(self) -> bool:
        """Check if the news plugin is healthy."""
        try:
            if not self.api_keys.get("news_api_key"):
                return False
            
            # Try a simple API call to verify connectivity
            test_data = await self._get_top_headlines(country="us", page_size=1)
            return test_data is not None and test_data.get("status") == "ok"
            
        except Exception:
            return False
