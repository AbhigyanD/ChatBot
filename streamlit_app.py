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
        return []

def main():
    st.set_page_config(
        page_title="TechPal - AI Learning Assistant",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for ChatGPT-like design
    st.markdown("""
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        background-color: #343541;
        color: white;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #202123;
    }
    
    /* Chat container */
    .chat-container {
        background-color: #343541;
        min-height: 100vh;
        padding: 0;
        margin: 0;
    }
    
    /* Message styling */
    .message {
        padding: 20px;
        margin: 0;
        border-bottom: 1px solid #40414f;
    }
    
    .user-message {
        background-color: #343541;
    }
    
    .assistant-message {
        background-color: #444654;
    }
    
    .message-content {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    .user-avatar {
        background-color: #10a37f;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 15px;
    }
    
    .assistant-avatar {
        background-color: #10a37f;
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 15px;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #343541;
        padding: 20px;
        border-top: 1px solid #40414f;
    }
    
    .input-wrapper {
        max-width: 800px;
        margin: 0 auto;
        position: relative;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #10a37f;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #0d8a6f;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #40414f;
        border: 1px solid #565869;
        border-radius: 6px;
        color: white;
        padding: 12px 16px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10a37f;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #202123;
        color: white;
    }
    
    /* Conversation list */
    .conversation-item {
        padding: 10px 15px;
        margin: 2px 0;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .conversation-item:hover {
        background-color: #2a2b32;
    }
    
    .conversation-item.active {
        background-color: #343541;
    }
    
    /* Welcome message */
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
        max-width: 600px;
        margin: 0 auto;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 20px;
        color: #ececf1;
    }
    
    .welcome-subtitle {
        font-size: 18px;
        color: #8e8ea0;
        margin-bottom: 30px;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-top: 40px;
    }
    
    .feature-card {
        background-color: #40414f;
        padding: 20px;
        border-radius: 8px;
        text-align: left;
    }
    
    .feature-icon {
        font-size: 24px;
        margin-bottom: 10px;
    }
    
    .feature-title {
        font-weight: 600;
        margin-bottom: 8px;
        color: #ececf1;
    }
    
    .feature-description {
        color: #8e8ea0;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0;">
            <h2 style="color: white; margin-bottom: 20px;">🚀 TechPal</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Age group selection
        age_group = st.selectbox(
            "Select your age group:",
            ["8-10", "11-13", "14-16"],
            help="This helps TechPal give you age-appropriate answers!"
        )
        
        # Session info
        session_id = generate_session_id()
        st.info(f"Session: {session_id[:8]}...")
        
        # New conversation button
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # Conversation history
        st.markdown("**Recent Conversations**")
        conversations = get_conversations(session_id)
        
        if conversations:
            for conv in conversations:
                title = conv.get('title', 'Conversation')[:30]
                if st.button(f"💬 {title}...", key=f"conv_{conv['id']}", use_container_width=True):
                    st.session_state.current_conversation_id = conv['id']
                    st.session_state.messages = []
                    st.rerun()
        else:
            st.info("No conversations yet")
    
    # Main chat area
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
    
    # Show welcome message if no messages
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-title">Welcome to TechPal</div>
            <div class="welcome-subtitle">Your AI learning assistant for technology, science, and school subjects</div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-title">Age-Appropriate Learning</div>
                    <div class="feature-description">Tailored responses for different age groups</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🛡️</div>
                    <div class="feature-title">Safe & Educational</div>
                    <div class="feature-description">Content filtering and educational focus</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🚀</div>
                    <div class="feature-title">Technology Topics</div>
                    <div class="feature-description">Computers, internet, coding, and more</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📚</div>
                    <div class="feature-title">School Subjects</div>
                    <div class="feature-description">Math, science, history with tech analogies</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message user-message">
                    <div class="message-content" style="display: flex; align-items: flex-start;">
                        <div class="user-avatar">U</div>
                        <div style="flex: 1; padding-top: 5px;">
                            {message["content"]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message assistant-message">
                    <div class="message-content" style="display: flex; align-items: flex-start;">
                        <div class="assistant-avatar">T</div>
                        <div style="flex: 1; padding-top: 5px;">
                            {message["content"]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Input area
    st.markdown("""
    <div class="input-container">
        <div class="input-wrapper">
    """, unsafe_allow_html=True)
    
    # Create columns for input and send button
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Message TechPal...",
            key="user_input",
            placeholder="Ask me anything about technology, science, or school subjects!",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", use_container_width=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
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
        else:
            # Remove the user message if API call failed
            st.session_state.messages.pop()
            st.error("Sorry, I'm having trouble connecting right now. Please try again!")

if __name__ == "__main__":
    main() 