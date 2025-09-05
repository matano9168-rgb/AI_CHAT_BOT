"""
Configuration management for the AI Chatbot application.
Handles environment variables, database connections, and API settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4", env="OPENAI_MODEL")
    openai_tts_model: str = Field("tts-1", env="OPENAI_TTS_MODEL")
    
    # Database Configuration
    mongodb_uri: str = Field("mongodb://localhost:27017", env="MONGODB_URI")
    mongodb_db_name: str = Field("chatbot_db", env="MONGODB_DB_NAME")
    
    # ChromaDB Configuration
    chroma_persist_directory: str = Field("./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API Keys for Plugins
    weather_api_key: Optional[str] = Field(None, env="WEATHER_API_KEY")
    news_api_key: Optional[str] = Field(None, env="NEWS_API_KEY")
    google_search_api_key: Optional[str] = Field(None, env="GOOGLE_SEARCH_API_KEY")
    google_search_cse_id: Optional[str] = Field(None, env="GOOGLE_SEARCH_CSE_ID")
    
    # Server Configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    debug: bool = Field(True, env="DEBUG")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
