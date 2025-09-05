"""
Memory management system for the AI Chatbot using simple in-memory storage.
Handles conversation context, document storage, and basic search.
"""

import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

from .config import settings


class MemoryManager:
    """Manages conversation memory and document storage using simple storage."""
    
    def __init__(self):
        self.conversations = {}
        self.documents = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize simple memory system."""
        try:
            # Ensure the persist directory exists
            os.makedirs(settings.chroma_persist_directory, exist_ok=True)
            
            # Load existing data if available
            self._load_data()
            self.initialized = True
            
            print("✅ Memory system initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize memory system: {e}")
            self.initialized = True  # Continue without persistent storage
    
    async def add_conversation_context(self, user_id: str, conversation_id: str, 
                                     messages: List[Dict[str, Any]]) -> bool:
        """Add conversation context to memory for future reference."""
        try:
            if not messages:
                return False
            
            # Create a summary of the conversation
            conversation_text = " ".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in messages[-10:]  # Last 10 messages for context
            ])
            
            # Generate unique ID for this context
            context_id = f"{conversation_id}_{uuid.uuid4().hex[:8]}"
            
            # Store in memory
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            self.conversations[user_id].append({
                "id": context_id,
                "conversation_id": conversation_id,
                "content": conversation_text,
                "timestamp": datetime.utcnow().isoformat(),
                "message_count": len(messages)
            })
            
            self._save_data()
            return True
            
        except Exception as e:
            print(f"Error adding conversation context: {e}")
            return False
    
    async def search_conversation_context(self, user_id: str, query: str, 
                                       limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant conversation context based on query."""
        try:
            if user_id not in self.conversations:
                return []
            
            # Simple keyword search
            query_lower = query.lower()
            contexts = []
            
            for conv in self.conversations[user_id]:
                if query_lower in conv['content'].lower():
                    contexts.append({
                        "content": conv['content'],
                        "metadata": {
                            "conversation_id": conv['conversation_id'],
                            "timestamp": conv['timestamp'],
                            "message_count": conv['message_count']
                        },
                        "distance": 0.5  # Mock distance
                    })
            
            return contexts[:limit]
            
        except Exception as e:
            print(f"Error searching conversation context: {e}")
            return []
    
    async def add_document(self, user_id: str, document_id: str, 
                          content: str, metadata: Dict[str, Any]) -> bool:
        """Add a document to the knowledge base."""
        try:
            # Split content into chunks for better retrieval
            chunks = self._split_text_into_chunks(content, chunk_size=1000, overlap=200)
            
            if user_id not in self.documents:
                self.documents[user_id] = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                self.documents[user_id].append({
                    "id": chunk_id,
                    "document_id": document_id,
                    "content": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                })
            
            self._save_data()
            return True
            
        except Exception as e:
            print(f"Error adding document: {e}")
            return False
    
    async def search_documents(self, query: str, user_id: Optional[str] = None, 
                             limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents based on query."""
        try:
            if user_id and user_id not in self.documents:
                return []
            
            query_lower = query.lower()
            documents = []
            
            docs_to_search = self.documents.get(user_id, []) if user_id else []
            for doc in docs_to_search:
                if query_lower in doc['content'].lower():
                    documents.append({
                        "content": doc['content'],
                        "metadata": doc['metadata'],
                        "distance": 0.5  # Mock distance
                    })
            
            return documents[:limit]
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    async def get_user_knowledge_base(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all documents in a user's knowledge base."""
        try:
            if user_id not in self.documents:
                return []
            
            documents = []
            for doc in self.documents[user_id]:
                documents.append({
                    "content": doc['content'],
                    "metadata": doc['metadata'],
                    "id": doc['id']
                })
            
            return documents
            
        except Exception as e:
            print(f"Error getting user knowledge base: {e}")
            return []
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete a document and all its chunks from the knowledge base."""
        try:
            if user_id not in self.documents:
                return False
            
            # Find and remove all chunks for this document
            original_count = len(self.documents[user_id])
            self.documents[user_id] = [
                doc for doc in self.documents[user_id] 
                if doc['document_id'] != document_id
            ]
            
            deleted = len(self.documents[user_id]) < original_count
            if deleted:
                self._save_data()
            
            return deleted
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, 
                               overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better retrieval."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunks.append(text[start:end])
            start = end - overlap
            
            # Ensure we don't go backwards
            if start <= 0:
                start = end
        
        return chunks
    
    async def get_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get statistics about the user's memory usage."""
        try:
            conversation_count = len(self.conversations.get(user_id, []))
            document_chunks = len(self.documents.get(user_id, []))
            
            # Count unique documents
            unique_docs = set()
            for doc in self.documents.get(user_id, []):
                unique_docs.add(doc['document_id'])
            document_count = len(unique_docs)
            
            return {
                "conversation_contexts": conversation_count,
                "document_chunks": document_chunks,
                "unique_documents": document_count,
                "total_memory_items": conversation_count + document_chunks
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {}
    
    async def cleanup_old_contexts(self, days_old: int = 30) -> int:
        """Clean up old conversation contexts to save memory."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            cutoff_iso = cutoff_date.isoformat()
            
            deleted_count = 0
            for user_id in self.conversations:
                original_count = len(self.conversations[user_id])
                self.conversations[user_id] = [
                    conv for conv in self.conversations[user_id]
                    if conv['timestamp'] > cutoff_iso
                ]
                deleted_count += original_count - len(self.conversations[user_id])
            
            if deleted_count > 0:
                self._save_data()
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up old contexts: {e}")
            return 0
    
    def _load_data(self):
        """Load data from persistent storage."""
        try:
            conv_file = os.path.join(settings.chroma_persist_directory, 'conversations.json')
            doc_file = os.path.join(settings.chroma_persist_directory, 'documents.json')
            
            if os.path.exists(conv_file):
                with open(conv_file, 'r') as f:
                    self.conversations = json.load(f)
            
            if os.path.exists(doc_file):
                with open(doc_file, 'r') as f:
                    self.documents = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def _save_data(self):
        """Save data to persistent storage."""
        try:
            conv_file = os.path.join(settings.chroma_persist_directory, 'conversations.json')
            doc_file = os.path.join(settings.chroma_persist_directory, 'documents.json')
            
            with open(conv_file, 'w') as f:
                json.dump(self.conversations, f)
            
            with open(doc_file, 'w') as f:
                json.dump(self.documents, f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    @property
    def client(self):
        """Mock client property for compatibility."""
        return self if self.initialized else None


# Global memory manager instance
memory_manager = MemoryManager()
