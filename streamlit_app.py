import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

def generate_session_id():
    """Generate a unique session ID for the user"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

def chat_with_techpal(message, session_id, conversation_id=None, age_group=None):
    """Send message to TechPal API"""
    url = f"{API_BASE_URL}/chat"
    payload = {
        "message": message,
        "session_id": session_id,
        "conversation_id": conversation_id,
        "age_group": age_group
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with TechPal: {e}")
        return None

def get_conversations(session_id):
    """Get user's conversation history"""
    url = f"{API_BASE_URL}/conversations/{session_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting conversations: {e}")
        return []

def main():
    st.set_page_config(
        page_title="TechPal - Your AI Learning Friend",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for child-friendly design
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: auto;
        text-align: right;
    }
    .assistant-message {
        background-color: #f3e5f5;
        margin-right: auto;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #5a6fd8 0%, #6a4190 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Welcome to TechPal!</h1>
        <p>Your friendly AI learning assistant for technology, science, and school subjects</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Age group selection
        age_group = st.selectbox(
            "What's your age group?",
            ["8-10", "11-13", "14-16"],
            help="This helps TechPal give you age-appropriate answers!"
        )
        
        # Session info
        session_id = generate_session_id()
        st.info(f"Session ID: {session_id[:8]}...")
        
        # New conversation button
        if st.button("🆕 Start New Conversation"):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        # Conversation history
        st.header("📚 Your Conversations")
        conversations = get_conversations(session_id)
        
        if conversations:
            for conv in conversations:
                if st.button(f"💬 {conv.get('title', 'Conversation')[:30]}...", key=f"conv_{conv['id']}"):
                    st.session_state.current_conversation_id = conv['id']
                    st.session_state.messages = []
                    st.rerun()
        else:
            st.info("No conversations yet. Start chatting to create one!")
    
    # Main chat area
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "current_conversation_id" not in st.session_state:
            st.session_state.current_conversation_id = None
        
        # Display chat messages
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>You:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>TechPal:</strong><br>
                        {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("---")
        
        # Quick questions for younger users
        if age_group in ["8-10", "11-13"]:
            st.subheader("💡 Quick Questions")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("How do computers work?"):
                    user_input = "How do computers work?"
                elif st.button("What is the internet?"):
                    user_input = "What is the internet?"
                elif st.button("How do I stay safe online?"):
                    user_input = "How do I stay safe online?"
                else:
                    user_input = None
                    
            with col2:
                if st.button("What is coding?"):
                    user_input = "What is coding?"
                elif st.button("How do robots work?"):
                    user_input = "How do robots work?"
                elif st.button("Can you help with math?"):
                    user_input = "Can you help me understand math better?"
                else:
                    user_input = None
        
        # Text input
        user_input = st.text_input(
            "Ask TechPal anything about technology, science, or school subjects!",
            key="user_input",
            placeholder="e.g., How do computers remember things?"
        )
        
        # Send button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            send_button = st.button("🚀 Send Message", use_container_width=True)
        
        # Process message
        if send_button and user_input:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Show typing indicator
            with st.spinner("TechPal is thinking..."):
                # Send to API
                response = chat_with_techpal(
                    user_input, 
                    session_id, 
                    st.session_state.current_conversation_id,
                    age_group
                )
            
            if response:
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["response"]
                })
                
                # Update conversation ID
                st.session_state.current_conversation_id = response["conversation_id"]
                
                # Clear input
                st.session_state.user_input = ""
                
                # Rerun to show new messages
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <p>🛡️ Remember: Always ask a parent or teacher if you're unsure about something online!</p>
        <p>TechPal is designed to help you learn safely and have fun with technology! 🚀</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 