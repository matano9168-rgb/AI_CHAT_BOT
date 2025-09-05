"""
Database models and connection management for the AI Chatbot.
Handles MongoDB connections and conversation storage.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from pydantic import BaseModel, Field
from bson import ObjectId
import json

from .config import settings


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def _get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string")


class Message(BaseModel):
    """Individual message in a conversation."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Conversation(BaseModel):
    """Complete conversation between user and chatbot."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(..., description="Unique identifier for the user")
    title: str = Field(..., description="Title of the conversation")
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(BaseModel):
    """User model for authentication and management."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str = Field(..., unique=True, description="Unique username")
    email: str = Field(..., unique=True, description="User email address")
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(True, description="Whether user account is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Database:
    """Database connection and operations manager."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
    
    async def connect(self):
        """Establish database connection."""
        try:
            self.client = AsyncIOMotorClient(settings.mongodb_uri)
            self.database = self.client[settings.mongodb_db_name]
            
            # Create indexes for better performance
            await self.database.conversations.create_index([("user_id", ASCENDING)])
            await self.database.conversations.create_index([("created_at", DESCENDING)])
            await self.database.users.create_index([("username", ASCENDING)])
            await self.database.users.create_index([("email", ASCENDING)])
            
            print("[OK] Connected to MongoDB successfully!")
        except Exception as e:
            print(f"[ERROR] Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            print("[OK] Disconnected from MongoDB")
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by ID."""
        try:
            conversation_data = await self.database.conversations.find_one(
                {"_id": ObjectId(conversation_id)}
            )
            if conversation_data:
                return Conversation(**conversation_data)
            return None
        except Exception as e:
            print(f"Error retrieving conversation: {e}")
            return None
    
    async def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Retrieve conversations for a specific user."""
        try:
            cursor = self.database.conversations.find(
                {"user_id": user_id}
            ).sort("updated_at", DESCENDING).limit(limit)
            
            conversations = []
            async for conversation_data in cursor:
                conversations.append(Conversation(**conversation_data))
            
            return conversations
        except Exception as e:
            print(f"Error retrieving user conversations: {e}")
            return []
    
    async def save_conversation(self, conversation: Conversation) -> str:
        """Save or update a conversation."""
        try:
            conversation.updated_at = datetime.utcnow()
            
            if conversation.id:
                # Update existing conversation
                await self.database.conversations.update_one(
                    {"_id": conversation.id},
                    {"$set": conversation.dict(exclude={"id"})}
                )
                return str(conversation.id)
            else:
                # Insert new conversation
                result = await self.database.conversations.insert_one(
                    conversation.dict(exclude={"id"})
                )
                return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving conversation: {e}")
            raise
    
    async def add_message_to_conversation(self, conversation_id: str, message: Message) -> bool:
        """Add a new message to an existing conversation."""
        try:
            result = await self.database.conversations.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$push": {"messages": message.dict()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error adding message to conversation: {e}")
            return False
    
    async def get_user(self, username: str) -> Optional[User]:
        """Retrieve a user by username."""
        try:
            user_data = await self.database.users.find_one({"username": username})
            if user_data:
                return User(**user_data)
            return None
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return None
    
    async def create_user(self, user: User) -> str:
        """Create a new user."""
        try:
            result = await self.database.users.insert_one(user.dict(exclude={"id"}))
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            raise
    
    async def update_user_last_login(self, username: str) -> bool:
        """Update user's last login timestamp."""
        try:
            result = await self.database.users.update_one(
                {"username": username},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user last login: {e}")
            return False


# Global database instance
database = Database()
