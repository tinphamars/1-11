import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from langchain_openai import AzureChatOpenAI, ChatOpenAI
except ImportError:
    from langchain_openai import ChatOpenAI
    AzureChatOpenAI = None
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Import OpenAI exceptions (v1.x structure)
try:
    from openai import APIError, APIConnectionError, AuthenticationError, RateLimitError
except ImportError:
    # Fallback for different OpenAI SDK versions
    try:
        from openai.error import APIError, APIConnectionError, AuthenticationError, RateLimitError
    except ImportError:
        # If exceptions not available, define base classes
        APIError = Exception
        APIConnectionError = ConnectionError
        AuthenticationError = ValueError
        RateLimitError = Exception

from app.core.config import Settings
from app.services.document_service import DocumentService

import os
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_TELEMETRY"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""


logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions with RAG."""

    def __init__(self, settings: Settings, document_service: DocumentService):
        self.settings = settings
        self.document_service = document_service

        # Initialize LLM based on configuration type
        if settings.openai_base_url and settings.openai_api_type.lower() == "azure":
            # Use AzureChatOpenAI if available, otherwise use ChatOpenAI with model_kwargs
            if AzureChatOpenAI is not None:
                logger.info(f"Initializing AzureChatOpenAI with endpoint: {settings.openai_base_url}, deployment: {settings.openai_model}")
                try:
                    self.llm = AzureChatOpenAI(
                        azure_deployment=settings.openai_model,
                        azure_endpoint=settings.openai_base_url,
                        openai_api_version=settings.openai_api_version,
                        openai_api_key=settings.openai_api_key,
                        temperature=settings.default_temperature,
                        max_tokens=settings.default_max_tokens
                    )
                    logger.info("AzureChatOpenAI initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize AzureChatOpenAI: {str(e)}")
                    raise ValueError(f"Failed to initialize AzureChatOpenAI: {str(e)}. Please check your Azure configuration.")
            else:
                # Fallback to ChatOpenAI with model_kwargs for Azure
                logger.info(f"Using ChatOpenAI for Azure with endpoint: {settings.openai_base_url}, deployment: {settings.openai_model}")
                try:
                    self.llm = ChatOpenAI(
                        openai_api_key=settings.openai_api_key,
                        temperature=settings.default_temperature,
                        max_tokens=settings.default_max_tokens,
                        model_kwargs={
                            "azure_endpoint": settings.openai_base_url,
                            "openai_api_version": settings.openai_api_version,
                            "azure_deployment": settings.openai_model
                        }
                    )
                    logger.info("ChatOpenAI (Azure) initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize ChatOpenAI for Azure: {str(e)}")
                    raise ValueError(f"Failed to initialize ChatOpenAI for Azure: {str(e)}. Please check your Azure configuration.")
        else:
            # Public OpenAI or compatible endpoint
            logger.info(f"Initializing ChatOpenAI with model: {settings.openai_model}")
            llm_kwargs = {
                "openai_api_key": settings.openai_api_key,
                "model": settings.openai_model,
                "temperature": settings.default_temperature,
                "max_tokens": settings.default_max_tokens
            }
            if settings.openai_base_url:
                llm_kwargs["openai_api_base"] = settings.openai_base_url
            
            try:
                self.llm = ChatOpenAI(**llm_kwargs)
                logger.info("ChatOpenAI initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize ChatOpenAI: {str(e)}")
                raise ValueError(f"Failed to initialize ChatOpenAI: {str(e)}. Please check your OpenAI configuration.")

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

        except (APIConnectionError, ConnectionError) as e:
            error_msg = f"Connection error: Unable to connect to OpenAI/Azure endpoint. Please check your network connection and endpoint URL ({self.settings.openai_base_url or 'default'})."
            logger.error(f"{error_msg} Details: {str(e)}")
            raise ConnectionError(error_msg) from e
        except AuthenticationError as e:
            error_msg = f"Authentication error: Invalid API key or credentials. Please check your OPENAI_API_KEY."
            logger.error(f"{error_msg} Details: {str(e)}")
            raise ValueError(error_msg) from e
        except RateLimitError as e:
            error_msg = f"Rate limit exceeded: Too many requests. Please try again later."
            logger.error(f"{error_msg} Details: {str(e)}")
            raise ValueError(error_msg) from e
        except APIError as e:
            error_msg = f"API error: {str(e)}"
            logger.error(f"{error_msg} Details: {str(e)}")
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error during chat: {str(e)}"
            logger.error(f"{error_msg}", exc_info=True)
            raise RuntimeError(error_msg) from e

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
        You are an expert AI onboarding assistant for the **RAG Chatbot API** project - a FastAPI-based system using Retrieval-Augmented Generation to answer questions from project documents. Your mission is to help new team members understand and contribute to this project quickly, reducing mentor workload by 80%+.

        ═══════════════════════════════════════════════════════════════════
        RELEVANT CONTEXT FROM PROJECT DOCUMENTS:
        ═══════════════════════════════════════════════════════════════════
        {context}

        ═══════════════════════════════════════════════════════════════════
        RESPONSE BEST PRACTICES:
        ═══════════════════════════════════════════════════════════════════

        1. **Always reference file paths** from the context when available
        2. **Show concrete code examples** with line numbers
        3. **Explain technical terms** (RAG, embeddings, vector search, chunking)
        4. **Provide step-by-step instructions** for setup/deployment tasks
        5. **Link related concepts**: "When you modify document_service.py, also check chat_service.py"
        6. **Anticipate follow-up questions**: "Next, you might want to know about..."
        7. **Cite sources** at the end: "*Reference: app/main.py:45-67, documents/Architecture.md*"
        8. **Use Vietnamese** for explanations if context suggests Vietnamese docs
        9. **Highlight common pitfalls**: Missing .env, wrong Docker port, ChromaDB path issues
        10. **Be encouraging**: "Great question! This is a key concept in RAG systems..."

        ═══════════════════════════════════════════════════════════════════
        YOUR ULTIMATE GOAL:
        ═══════════════════════════════════════════════════════════════════

        Make new developers **productive in 30 minutes instead of 3 days**. Answer questions that would typically require:
        - 2-3 hours of senior developer time
        - Reading through multiple documentation files
        - Trial-and-error experimentation
        - Understanding complex RAG/LLM concepts

        You are the **first line of support** - only escalate to human mentors when:
        - Bug in production code that needs immediate fix
        - Architecture decisions requiring team discussion
        - Access/permission issues
        - Information truly not available in project docs

        **Remember:** You have deep knowledge of this specific RAG Chatbot API project. Use it fully!
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

