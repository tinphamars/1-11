import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from app.core.config import Settings
from app.services.document_service import DocumentService

import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TELEMETRY"] = "false"


logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions with RAG."""

    def __init__(self, settings: Settings, document_service: DocumentService):
        self.settings = settings
        self.document_service = document_service

        # Initialize LLM
     
        llm_kwargs = {
            "openai_api_key": settings.openai_api_key,
            "temperature": settings.default_temperature,
            "max_tokens": settings.default_max_tokens
        }

        # Azure vs Public OpenAI configuration
        if settings.openai_base_url and settings.openai_api_type.lower() == "azure":
            llm_kwargs["azure_endpoint"] = settings.openai_base_url
            llm_kwargs["openai_api_version"] = settings.openai_api_version
            llm_kwargs["azure_deployment"] = settings.openai_model  # deployment name
        else:
            # Public OpenAI or compatible endpoint
            llm_kwargs["model"] = settings.openai_model
            if settings.openai_base_url:
                llm_kwargs["openai_api_base"] = settings.openai_base_url

        self.llm = ChatOpenAI(**llm_kwargs)

        # Store conversations in memory
        # (In production, this should be replaced with a database)
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}

    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """Handle chat interaction with RAG."""
        # Generate conversation ID if not provided
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        # Set parameters
        max_tokens = max_tokens or self.settings.default_max_tokens
        temperature = temperature or self.settings.default_temperature

        try:
            # Search for relevant documents
            similar_docs = await self.document_service.search_similar_documents(
                query=message,
                k=self.settings.retrieval_k
            )

            # Build context from retrieved documents
            context = self.build_context(similar_docs)

            # Get conversation history
            conversation_history = self.conversations.get(conversation_id, [])

            # Create prompt with context and history
            system_prompt = self._create_system_prompt(context)
            messages = self._build_messages(system_prompt, conversation_history, message)

            # Update LLM parameters
            self.llm.temperature = temperature
            self.llm.max_tokens = max_tokens

            # Generate response
            response = await self.llm.agenerate([messages])
            ai_response = response.generations[0][0].text

            # Update conversation history
            self._update_conversation(conversation_id, message, ai_response)

            # Prepare sources information
            sources = self._format_sources(similar_docs)

            return {
                "answer": ai_response,
                "conversation_id": conversation_id,
                "sources": sources,
                "metadata": {
                    "retrieved_documents": len(similar_docs),
                    "timestamp": datetime.now().isoformat(),
                    "model": self.settings.openai_model,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }

        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise

    def build_context(self, similar_docs: List[Dict[str, Any]]) -> str:
        """Build context string from retrieved documents."""
        if not similar_docs:
            return "No relevant documents found."

        context_parts = []
        for i, doc in enumerate(similar_docs, 1):
            source = doc["metadata"].get("source", "Unknown")
            content = doc["content"][:500]  # limit content length
            context_parts.append(f"Document {i} (from {source}):\n{content}\n")

        return "\n---\n".join(context_parts)

    def _create_system_prompt(self, context: str) -> str:
        """Create system prompt with context."""
        return f"""
You are a helpful AI assistant that answers questions about a software project.

Context from the project documents:
{context}

Instructions:
1. Answer questions based primarily on the provided context.
2. If information is not available in the context, clearly state that.
3. Provide specific examples from the code when relevant.
4. Help with installation, setup, and usage questions.
5. Be concise but comprehensive in your responses.
6. If asked about code, reference the specific files when possible.
"""

    def _build_messages(
        self,
        system_prompt: str,
        history: List[Dict[str, Any]],
        current_message: str
    ) -> List[Any]:
        """Build message list for LLM."""
        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history (limit to relevant messages)
        max_history = self.settings.max_conversation_length
        recent_history = history[-max_history:] if len(history) > max_history else history

        for msg in recent_history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=current_message))
        return messages

    def _update_conversation(self, conversation_id: str, user_message: str, ai_response: str):
        """Update conversation history."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        conversation = self.conversations[conversation_id]

        # Add user message
        conversation.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        # Add AI response
        conversation.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })

        # Limit conversation length
        max_length = self.settings.max_conversation_length * 2  # *2 for user+assistant pairs
        if len(conversation) > max_length:
            self.conversations[conversation_id] = conversation[-max_length:]

    def _format_sources(self, similar_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source documents for response."""
        sources = []
        for doc in similar_docs:
            metadata = doc.get("metadata", {})
            sources.append({
                "file_path": metadata.get("source", "Unknown"),
                "file_name": metadata.get("file_name", "Unknown"),
                "file_type": metadata.get("file_type", "Unknown"),
                "relevance_score": round(doc.get("score", 0.0), 3),
                "content_preview": (
                    doc["content"][:200] + "..."
                    if len(doc.get("content", "")) > 200
                    else doc.get("content", "")
                )
            })
        return sources

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversations.get(conversation_id, [])

    def clear_conversation(self, conversation_id: str):
        """Clear a specific conversation."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]

    def list_conversations(self) -> List[str]:
        """List all conversation IDs."""
        return list(self.conversations.keys())

