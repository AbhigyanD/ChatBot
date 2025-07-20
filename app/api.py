from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import uuid
from datetime import datetime

from app.database import get_db
from app.models import User, Conversation, Message, ChatRequest, ChatResponse, ConversationResponse
from app.crud import (
    get_or_create_user, 
    create_conversation, 
    get_conversation, 
    get_user_conversations,
    add_message_to_conversation
)
from app.llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TechPal API",
    description="AI Learning Assistant for Children",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM service
llm_service = LLMService()

@app.on_event("startup")
async def startup_event():
    logger.info("TechPal API started successfully!")

@app.get("/")
async def root():
    return {
        "message": "Welcome to TechPal API!",
        "description": "AI Learning Assistant for Children",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": "TechPal",
        "version": "1.0.0",
        "llm_providers": {
            "openai": llm_service.openai_client is not None,
            "anthropic": llm_service.anthropic_client is not None
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat endpoint for TechPal interactions"""
    try:
        # Validate user message
        validation = llm_service.validate_message(request.message)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["reason"])
        
        # Get or create user
        user = get_or_create_user(db, request.session_id)
        
        # Get or create conversation
        conversation = None
        if request.conversation_id:
            conversation = get_conversation(db, request.conversation_id, user.id)
        
        if not conversation:
            conversation = create_conversation(db, user.id, request.message[:50] + "...")
        
        # Add user message to conversation
        user_message = add_message_to_conversation(
            db, 
            conversation.id, 
            "user", 
            request.message
        )
        
        # Get AI response
        try:
            ai_response = llm_service.get_response(
                request.message, 
                request.age_group or "11-13"
            )
        except Exception as e:
            logger.error(f"Error in chat endpoint: {e}")
            # Use fallback response if API fails
            ai_response = llm_service._get_fallback_response(
                request.message, 
                request.age_group or "11-13"
            )
        
        # Add AI response to conversation
        ai_message = add_message_to_conversation(
            db, 
            conversation.id, 
            "assistant", 
            ai_response
        )
        
        # Update conversation title if it's the first message
        if len(conversation.messages) <= 2:  # Just the user and AI messages
            conversation.title = request.message[:50] + "..."
            db.commit()
        
        return ChatResponse(
            response=ai_response,
            conversation_id=str(conversation.id),
            message_id=str(ai_message.id),
            timestamp=ai_message.timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{session_id}", response_model=List[ConversationResponse])
async def get_conversations(session_id: str, db: Session = Depends(get_db)):
    """Get all conversations for a user session"""
    try:
        user = get_or_create_user(db, session_id)
        conversations = get_user_conversations(db, user.id)
        
        return [
            ConversationResponse(
                id=str(conv.id),
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=len(conv.messages)
            )
            for conv in conversations
        ]
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversation/{conversation_id}")
async def get_conversation_messages(conversation_id: str, session_id: str, db: Session = Depends(get_db)):
    """Get messages for a specific conversation"""
    try:
        user = get_or_create_user(db, session_id)
        conversation = get_conversation(db, conversation_id, user.id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": [
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in conversation.messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 