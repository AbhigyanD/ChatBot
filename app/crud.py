from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import uuid

from app.models import User, Conversation, Message
from app.models import UserCreate, ConversationCreate, MessageCreate

def create_user(db: Session, user_create: UserCreate) -> User:
    """Create a new user"""
    db_user = User(
        session_id=user_create.session_id,
        age_group=user_create.age_group
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_session_id(db: Session, session_id: str) -> Optional[User]:
    """Get user by session ID"""
    return db.query(User).filter(User.session_id == session_id).first()

def get_or_create_user(db: Session, session_id: str, age_group: Optional[str] = None) -> User:
    """Get existing user or create new one"""
    user = get_user_by_session_id(db, session_id)
    if not user:
        user_create = UserCreate(session_id=session_id, age_group=age_group)
        user = create_user(db, user_create)
    return user

def create_conversation(db: Session, user_id: int, title: Optional[str] = None) -> Conversation:
    """Create a new conversation"""
    if not title:
        title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    db_conversation = Conversation(
        user_id=user_id,
        title=title
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
    """Get conversation by ID"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_user_conversations(db: Session, user_id: int, limit: int = 10) -> List[Conversation]:
    """Get conversations for a user"""
    return db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(desc(Conversation.updated_at))\
        .limit(limit)\
        .all()

def create_message(db: Session, conversation_id: int, content: str, role: str, 
                  tokens_used: int = 0, llm_provider: str = "unknown") -> Message:
    """Create a new message"""
    db_message = Message(
        conversation_id=conversation_id,
        content=content,
        role=role,
        tokens_used=tokens_used,
        llm_provider=llm_provider
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_conversation_messages(db: Session, conversation_id: int) -> List[Message]:
    """Get all messages for a conversation"""
    return db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at)\
        .all()

def update_conversation_timestamp(db: Session, conversation_id: int):
    """Update conversation's updated_at timestamp"""
    conversation = get_conversation(db, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        db.commit()

def delete_conversation(db: Session, conversation_id: int) -> bool:
    """Delete a conversation and all its messages"""
    conversation = get_conversation(db, conversation_id)
    if conversation:
        # Delete all messages first
        db.query(Message).filter(Message.conversation_id == conversation_id).delete()
        # Delete conversation
        db.delete(conversation)
        db.commit()
        return True
    return False

def get_conversation_history(db: Session, conversation_id: int) -> List[dict]:
    """Get conversation history as list of dicts for LLM"""
    messages = get_conversation_messages(db, conversation_id)
    return [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in messages
    ]

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4()) 