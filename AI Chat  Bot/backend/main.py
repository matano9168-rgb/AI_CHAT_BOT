"""
Main FastAPI application for the AI Chatbot.
Provides REST API endpoints for chat, authentication, and file management.
"""

import asyncio
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import tempfile
from typing import List, Optional
import json
from datetime import datetime

from .config import settings
from .database import database, Conversation, Message
from .memory import memory_manager
from .chatbot import chatbot_engine
from .auth import auth_manager, get_current_active_user, UserCreate, UserLogin, Token
from .plugins.base import plugin_manager

# Create FastAPI app
app = FastAPI(
    title="AI Chatbot API",
    description="Professional-grade chatbot with AI, memory, and plugins",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        print("[STARTING] AI Chatbot...")
        
        # Initialize database
        await database.connect()
        print("[OK] Database connected")
        
        # Initialize memory system
        await memory_manager.initialize()
        print("[OK] Memory system initialized")
        
        # Register plugins
        from .plugins.weather import WeatherPlugin
        from .plugins.news import NewsPlugin
        from .plugins.wikipedia import WikipediaPlugin
        
        plugin_manager.register_plugin(WeatherPlugin())
        plugin_manager.register_plugin(NewsPlugin())
        plugin_manager.register_plugin(WikipediaPlugin())
        print("[OK] Plugins registered")
        
        print("[SUCCESS] AI Chatbot started successfully!")
        
    except Exception as e:
        print(f"[ERROR] Failed to start AI Chatbot: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        print("[SHUTDOWN] Shutting down AI Chatbot...")
        await database.disconnect()
        print("[OK] Database disconnected")
        print("[OK] AI Chatbot shutdown complete")
    except Exception as e:
        print(f"[ERROR] Error during shutdown: {e}")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        db_healthy = database.client is not None
        
        # Check memory system
        memory_healthy = memory_manager.client is not None
        
        # Check plugins
        plugin_health = await plugin_manager.health_check_all()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "database": db_healthy,
                "memory": memory_healthy,
                "plugins": plugin_health
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }


# Authentication endpoints
@app.post("/auth/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Register a new user."""
    try:
        user = await auth_manager.register_user(user_data)
        return {
            "message": "User registered successfully",
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/login", response_model=Token)
async def login_user(user_data: UserLogin):
    """Authenticate and login a user."""
    try:
        return await auth_manager.login_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Chat endpoints
@app.post("/chat/send")
async def send_message(
    message: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    current_user = Depends(get_current_active_user)
):
    """Send a message to the chatbot."""
    try:
        # Process the message
        response = await chatbot_engine.process_message(
            user_id=str(current_user.id),
            message=message,
            conversation_id=conversation_id
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/conversations")
async def get_conversations(
    limit: int = 20,
    current_user = Depends(get_current_active_user)
):
    """Get user's conversation history."""
    try:
        conversations = await chatbot_engine.get_conversation_history(
            user_id=str(current_user.id),
            limit=limit
        )
        
        # Convert to serializable format
        serialized_conversations = []
        for conv in conversations:
            serialized_conv = {
                "id": str(conv.id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": len(conv.messages)
            }
            serialized_conversations.append(serialized_conv)
        
        return {"conversations": serialized_conversations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get a specific conversation."""
    try:
        conversation = await database.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert to serializable format
        serialized_messages = []
        for msg in conversation.messages:
            serialized_msg = {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            serialized_messages.append(serialized_msg)
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": serialized_messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chat/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user = Depends(get_current_active_user)
):
    """Delete a conversation."""
    try:
        conversation = await database.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete from database
        result = await database.database.conversations.delete_one(
            {"_id": conversation.id}
        )
        
        if result.deleted_count > 0:
            return {"message": "Conversation deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete conversation")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# File upload and management endpoints
@app.post("/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user = Depends(get_current_active_user)
):
    """Upload a file to the knowledge base."""
    try:
        # Validate file type
        allowed_extensions = {'.txt', '.pdf', '.docx', '.md'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        
        if file_extension == '.txt' or file_extension == '.md':
            text_content = content.decode('utf-8')
        elif file_extension == '.pdf':
            # Handle PDF files
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        elif file_extension == '.docx':
            # Handle DOCX files
            from docx import Document
            import io
            doc = Document(io.BytesIO(content))
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Add to knowledge base
        document_id = f"{current_user.username}_{file.filename}_{datetime.now().timestamp()}"
        
        success = await memory_manager.add_document(
            user_id=str(current_user.id),
            document_id=document_id,
            content=text_content,
            metadata={
                "filename": file.filename,
                "file_type": file_extension,
                "file_size": len(content),
                "uploaded_at": datetime.now().isoformat()
            }
        )
        
        if success:
            return {
                "message": "File uploaded successfully",
                "document_id": document_id,
                "filename": file.filename,
                "content_length": len(text_content)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add file to knowledge base")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/knowledge-base")
async def get_knowledge_base(
    current_user = Depends(get_current_active_user)
):
    """Get user's knowledge base documents."""
    try:
        documents = await memory_manager.get_user_knowledge_base(
            user_id=str(current_user.id)
        )
        
        # Format response
        formatted_docs = []
        for doc in documents:
            formatted_doc = {
                "id": doc["id"],
                "content_preview": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                "metadata": doc["metadata"]
            }
            formatted_docs.append(formatted_doc)
        
        return {"documents": formatted_docs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{document_id}")
async def delete_document(
    document_id: str,
    current_user = Depends(get_current_active_user)
):
    """Delete a document from the knowledge base."""
    try:
        success = await memory_manager.delete_document(
            document_id=document_id,
            user_id=str(current_user.id)
        )
        
        if success:
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export endpoints
@app.get("/export/conversation/{conversation_id}")
async def export_conversation(
    conversation_id: str,
    format: str = "txt",
    current_user = Depends(get_current_active_user)
):
    """Export a conversation in the specified format."""
    try:
        # Verify access
        conversation = await database.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Export conversation
        exported_content = await chatbot_engine.export_conversation(
            conversation_id, format
        )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format}') as f:
            f.write(exported_content)
            temp_file_path = f.name
        
        # Return file response
        filename = f"conversation_{conversation_id}.{format}"
        
        return FileResponse(
            path=temp_file_path,
            filename=filename,
            media_type='text/plain' if format == 'txt' else 'application/json'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Plugin endpoints
@app.get("/plugins")
async def get_plugins():
    """Get available plugins and their capabilities."""
    try:
        available_plugins = plugin_manager.get_available_plugins()
        plugin_info = []
        
        for plugin in available_plugins:
            plugin_info.append({
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "capabilities": plugin.get_capabilities(),
                "help_text": plugin.get_help_text(),
                "usage_examples": plugin.get_usage_examples()
            })
        
        return {"plugins": plugin_info}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plugins/{plugin_name}/execute")
async def execute_plugin(
    plugin_name: str,
    params: dict,
    current_user = Depends(get_current_active_user)
):
    """Execute a specific plugin."""
    try:
        result = await plugin_manager.execute_plugin(plugin_name, **params)
        return result.dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# User management endpoints
@app.get("/users/profile")
async def get_user_profile(
    current_user = Depends(get_current_active_user)
):
    """Get current user's profile."""
    try:
        # Get memory stats
        memory_stats = await memory_manager.get_memory_stats(
            user_id=str(current_user.id)
        )
        
        return {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email,
            "created_at": current_user.created_at.isoformat(),
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "is_active": current_user.is_active,
            "memory_stats": memory_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user = Depends(get_current_active_user)
):
    """Change user password."""
    try:
        success = await auth_manager.change_password(
            current_user, current_password, new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
