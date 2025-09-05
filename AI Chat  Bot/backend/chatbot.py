"""
Core chatbot engine for the AI Chatbot application.
Integrates OpenAI, memory management, and plugins for intelligent conversations.
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import openai
from openai import AsyncOpenAI

from .config import settings
from .database import Message, Conversation, database
from .memory import memory_manager
from .plugins.base import plugin_manager, PluginResponse


class ChatbotEngine:
    """Main chatbot engine that handles conversations and AI responses."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        # Initialize plugins with API keys
        self._initialize_plugins()
    
    def _initialize_plugins(self):
        """Initialize all plugins with their required API keys."""
        try:
            # Weather plugin
            weather_plugin = plugin_manager.get_plugin("weather")
            if weather_plugin:
                weather_plugin.set_api_key("weather_api_key", settings.weather_api_key)
            
            # News plugin
            news_plugin = plugin_manager.get_plugin("news")
            if news_plugin:
                news_plugin.set_api_key("news_api_key", settings.news_api_key)
            
            # Wikipedia plugin (no API key needed)
            wikipedia_plugin = plugin_manager.get_plugin("wikipedia")
            
            print(f"[OK] Initialized {len(plugin_manager.plugins)} plugins: {', '.join(plugin_manager.plugins.keys())}")
        except Exception as e:
            print(f"[ERROR] Error initializing plugins: {e}")
    
    async def process_message(self, user_id: str, message: str, 
                            conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a user message and generate a response."""
        try:
            # Check for plugin commands
            plugin_response = await self._check_for_plugin_commands(message)
            if plugin_response:
                return {
                    "response": plugin_response,
                    "conversation_id": conversation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "plugin_response"
                }
            
            # Get conversation context
            conversation = await self._get_or_create_conversation(
                user_id, conversation_id, message
            )
            
            # Search for relevant context from memory
            context = await self._get_relevant_context(user_id, message)
            
            # Generate AI response
            ai_response = await self._generate_ai_response(
                message, conversation, context
            )
            
            # Save the conversation
            conversation_id = await self._save_conversation(conversation, message, ai_response)
            
            # Add to memory for future reference
            await memory_manager.add_conversation_context(
                user_id, conversation_id, conversation.messages
            )
            
            return {
                "response": ai_response,
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "ai_response"
            }
            
        except Exception as e:
            print(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your message. Please try again.",
                "conversation_id": conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "error"
            }
    
    async def _check_for_plugin_commands(self, message: str) -> Optional[str]:
        """Check if the message contains plugin commands and execute them."""
        try:
            # Simple pattern matching for plugin commands
            # This could be enhanced with more sophisticated NLP
            plugin_patterns = {
                r"weather\s+(?:in|for)\s+([^.!?]+)": ("weather", {"location": r"\1"}),
                r"news\s+(?:about|on)\s+([^.!?]+)": ("news", {"query": r"\1"}),
                r"search\s+wikipedia\s+for\s+([^.!?]+)": ("wikipedia", {"query": r"\1"}),
                r"tell\s+me\s+about\s+([^.!?]+)": ("wikipedia", {"query": r"\1"}),
            }
            
            for pattern, (plugin_name, params) in plugin_patterns.items():
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    # Extract parameters
                    extracted_params = {}
                    for key, value_pattern in params.items():
                        if isinstance(value_pattern, str) and value_pattern.startswith("\\"):
                            # This is a regex group reference
                            group_num = int(value_pattern[1:])
                            extracted_params[key] = match.group(group_num).strip()
                        else:
                            extracted_params[key] = value_pattern
                    
                    # Execute plugin
                    plugin_result = await plugin_manager.execute_plugin(
                        plugin_name, **extracted_params
                    )
                    
                    if plugin_result.success:
                        return self._format_plugin_response(plugin_name, plugin_result.data)
                    else:
                        return f"Plugin error: {plugin_result.error}"
            
            return None
            
        except Exception as e:
            print(f"Error checking plugin commands: {e}")
            return None
    
    def _format_plugin_response(self, plugin_name: str, data: Dict[str, Any]) -> str:
        """Format plugin response data into a readable string."""
        try:
            if plugin_name == "weather":
                return self._format_weather_response(data)
            elif plugin_name == "news":
                return self._format_news_response(data)
            elif plugin_name == "wikipedia":
                return self._format_wikipedia_response(data)
            else:
                return str(data)
                
        except Exception as e:
            print(f"Error formatting plugin response: {e}")
            return str(data)
    
    def _format_weather_response(self, data: Dict[str, Any]) -> str:
        """Format weather data into a readable response."""
        try:
            temp = data.get("temperature", {})
            wind = data.get("wind", {})
            
            response = f"🌤️ Weather in {data.get('location', 'Unknown')}:\n"
            response += f"• Current: {temp.get('current', 'N/A')}\n"
            response += f"• Feels like: {temp.get('feels_like', 'N/A')}\n"
            response += f"• Humidity: {data.get('humidity', 'N/A')}\n"
            response += f"• Wind: {wind.get('speed', 'N/A')}\n"
            response += f"• Description: {data.get('weather_description', 'N/A')}"
            
            return response
            
        except Exception as e:
            print(f"Error formatting weather response: {e}")
            return str(data)
    
    def _format_news_response(self, data: Dict[str, Any]) -> str:
        """Format news data into a readable response."""
        try:
            articles = data.get("articles", [])
            if not articles:
                return "No news articles found."
            
            response = f"📰 Found {len(articles)} news articles:\n\n"
            
            for i, article in enumerate(articles[:3], 1):  # Show first 3 articles
                response += f"{i}. **{article.get('title', 'No title')}**\n"
                response += f"   {article.get('description', 'No description')}\n"
                response += f"   Source: {article.get('source', 'Unknown')}\n\n"
            
            return response
            
        except Exception as e:
            print(f"Error formatting news response: {e}")
            return str(data)
    
    def _format_wikipedia_response(self, data: Dict[str, Any]) -> str:
        """Format Wikipedia data into a readable response."""
        try:
            if "results" in data:
                # Search results
                results = data.get("results", [])
                if not results:
                    return "No Wikipedia articles found."
                
                response = f"🔍 Found {len(results)} Wikipedia articles:\n\n"
                
                for i, result in enumerate(results[:3], 1):  # Show first 3 results
                    response += f"{i}. **{result.get('title', 'No title')}**\n"
                    response += f"   {result.get('description', 'No description')}\n\n"
                
                return response
            else:
                # Single article
                response = f"📚 **{data.get('title', 'No title')}**\n\n"
                response += f"{data.get('extract', 'No content available')}\n\n"
                response += f"Read more: {data.get('url', 'No URL available')}"
                
                return response
                
        except Exception as e:
            print(f"Error formatting Wikipedia response: {e}")
            return str(data)
    
    async def _get_or_create_conversation(self, user_id: str, 
                                        conversation_id: Optional[str], 
                                        message: str) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id:
            conversation = await database.get_conversation(conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation
        
        # Create new conversation
        title = message[:50] + "..." if len(message) > 50 else message
        conversation = Conversation(
            user_id=user_id,
            title=title,
            messages=[]
        )
        
        return conversation
    
    async def _get_relevant_context(self, user_id: str, message: str) -> str:
        """Get relevant context from memory based on the current message."""
        try:
            # Search for relevant conversation context
            context_results = await memory_manager.search_conversation_context(
                user_id, message, limit=3
            )
            
            # Search for relevant documents
            document_results = await memory_manager.search_documents(
                message, user_id, limit=2
            )
            
            context_parts = []
            
            # Add conversation context
            if context_results:
                context_parts.append("Previous conversation context:")
                for context in context_results:
                    context_parts.append(f"- {context['content'][:200]}...")
            
            # Add document context
            if document_results:
                context_parts.append("Relevant knowledge base information:")
                for doc in document_results:
                    context_parts.append(f"- {doc['content'][:200]}...")
            
            return "\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            print(f"Error getting relevant context: {e}")
            return ""
    
    async def _generate_ai_response(self, message: str, conversation: Conversation, 
                                  context: str) -> str:
        """Generate AI response using OpenAI."""
        try:
            # Build conversation history for context
            messages = []
            
            # Add system message with context
            system_content = (
                "You are a helpful, intelligent AI assistant. "
                "You can help with any topic and have access to various tools and knowledge. "
                "Be conversational, helpful, and accurate in your responses. "
                "If you're not sure about something, say so rather than guessing."
            )
            
            if context:
                system_content += f"\n\nRelevant context:\n{context}"
            
            messages.append({"role": "system", "content": system_content})
            
            # Add recent conversation history
            for msg in conversation.messages[-6:]:  # Last 6 messages for context
                messages.append({"role": msg.role, "content": msg.content})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Generate response using OpenAI
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            if response.choices and response.choices[0].message:
                ai_response = response.choices[0].message.content
                return ai_response.strip()
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I apologize, but I encountered an error generating a response. Please try again."
    
    async def _save_conversation(self, conversation: Conversation, 
                               user_message: str, ai_response: str) -> str:
        """Save the conversation to the database."""
        try:
            # Add user message
            user_msg = Message(
                role="user",
                content=user_message,
                timestamp=datetime.utcnow()
            )
            conversation.messages.append(user_msg)
            
            # Add AI response
            ai_msg = Message(
                role="assistant",
                content=ai_response,
                timestamp=datetime.utcnow()
            )
            conversation.messages.append(ai_msg)
            
            # Save to database
            conversation_id = await database.save_conversation(conversation)
            return conversation_id
            
        except Exception as e:
            print(f"Error saving conversation: {e}")
            raise
    
    async def get_conversation_history(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Get conversation history for a user."""
        try:
            return await database.get_user_conversations(user_id, limit)
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    async def export_conversation(self, conversation_id: str, format: str = "txt") -> str:
        """Export a conversation in the specified format."""
        try:
            conversation = await database.get_conversation(conversation_id)
            if not conversation:
                raise ValueError("Conversation not found")
            
            if format.lower() == "txt":
                return self._export_to_txt(conversation)
            elif format.lower() == "json":
                return self._export_to_json(conversation)
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            print(f"Error exporting conversation: {e}")
            raise
    
    def _export_to_txt(self, conversation: Conversation) -> str:
        """Export conversation to plain text format."""
        lines = [
            f"Conversation: {conversation.title}",
            f"Created: {conversation.created_at}",
            f"Updated: {conversation.updated_at}",
            "=" * 50,
            ""
        ]
        
        for message in conversation.messages:
            role = "User" if message.role == "user" else "Assistant"
            lines.append(f"{role}: {message.content}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _export_to_json(self, conversation: Conversation) -> str:
        """Export conversation to JSON format."""
        export_data = {
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in conversation.messages
            ]
        }
        
        return json.dumps(export_data, indent=2)


# Global chatbot engine instance
chatbot_engine = ChatbotEngine()
