from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db, create_tables
from app.models import (
    ChatRequest, ChatResponse, ConversationResponse, 
    UserResponse, MessageResponse
)
from app.crud import (
    get_or_create_user, create_conversation, get_conversation,
    get_user_conversations, create_message, get_conversation_history,
    update_conversation_timestamp, delete_conversation
)
from app.llm_service import llm_service
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="TechPal - Educational AI Assistant for Children",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_tables()
    logger.info("TechPal API started successfully!")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with welcome message"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TechPal - Educational AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f0f8ff; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c5aa0; text-align: center; }
            .feature { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            .api-link { color: #007bff; text-decoration: none; }
            .api-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Welcome to TechPal!</h1>
            <p>TechPal is an educational AI assistant designed to help children (ages 8-16) learn about technology, science, and school subjects in a safe and engaging way.</p>
            
            <div class="feature">
                <h3>🎯 What TechPal Does:</h3>
                <ul>
                    <li>Explains technology concepts in simple, age-appropriate language</li>
                    <li>Helps with school subjects using tech analogies</li>
                    <li>Promotes internet safety and digital citizenship</li>
                    <li>Encourages critical thinking and curiosity</li>
                    <li>Provides hands-on learning suggestions</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🔗 API Endpoints:</h3>
                <ul>
                    <li><a href="/docs" class="api-link">Interactive API Documentation</a></li>
                    <li><a href="/chat" class="api-link">Chat with TechPal</a></li>
                    <li><a href="/conversations" class="api-link">View Conversations</a></li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🛡️ Safety Features:</h3>
                <ul>
                    <li>Content filtering for age-appropriate responses</li>
                    <li>No personal information collection</li>
                    <li>Educational focus with safety reminders</li>
                    <li>Encouragement to discuss with parents/teachers</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/chat", response_model=ChatResponse)
async def chat_with_techpal(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with TechPal - the main endpoint for interacting with the AI assistant
    """
    try:
        # Validate user message
        if not llm_service.validate_message(request.message):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message contains inappropriate content for children"
            )
        
        # Get or create user
        user = get_or_create_user(db, request.session_id, request.age_group)
        
        # Get or create conversation
        if request.conversation_id:
            conversation = get_conversation(db, request.conversation_id)
            if not conversation or conversation.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation with title based on first message
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation = create_conversation(db, user.id, title)
        
        # Save user message
        user_message = create_message(
            db, conversation.id, request.message, "user"
        )
        
        # Get conversation history for context
        history = get_conversation_history(db, conversation.id)
        
        # Get response from LLM
        response_content, tokens_used, provider = llm_service.get_response(history)
        
        # Save assistant response
        assistant_message = create_message(
            db, conversation.id, response_content, "assistant", 
            tokens_used, provider
        )
        
        # Update conversation timestamp
        update_conversation_timestamp(db, conversation.id)
        
        return ChatResponse(
            response=response_content,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            tokens_used=tokens_used,
            llm_provider=provider
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )

@app.get("/conversations/{session_id}", response_model=List[ConversationResponse])
async def get_conversations(
    session_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all conversations for a user session"""
    try:
        user = get_or_create_user(db, session_id)
        conversations = get_user_conversations(db, user.id, limit)
        return conversations
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}"
        )

@app.get("/conversations/{session_id}/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_details(
    session_id: str,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed conversation with all messages"""
    try:
        user = get_or_create_user(db, session_id)
        conversation = get_conversation(db, conversation_id)
        
        if not conversation or conversation.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return conversation
    except Exception as e:
        logger.error(f"Error getting conversation details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation details: {str(e)}"
        )

@app.delete("/conversations/{session_id}/{conversation_id}")
async def delete_conversation_endpoint(
    session_id: str,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation"""
    try:
        user = get_or_create_user(db, session_id)
        conversation = get_conversation(db, conversation_id)
        
        if not conversation or conversation.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        success = delete_conversation(db, conversation_id)
        if success:
            return {"message": "Conversation deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "llm_providers": {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 