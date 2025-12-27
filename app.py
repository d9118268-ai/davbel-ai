# ========================================
# DAVBEL AI - COMPLETE CHATBOT APP
# Gemini-Style UI with Supabase Backend
# ========================================

# INSTALLATION (Run this first in a cell):
# !pip install streamlit google-generativeai supabase python-dotenv

import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from datetime import datetime
import hashlib
import re

# ========================================
# CONFIGURATION
# ========================================

# Gemini API Key
GEMINI_API_KEY = "AIzaSyA_J6kV5z19e4RyjpysjnUd5nwEkpg07Ik"  # Replace with your Gemini API key

# Supabase Configuration
SUPABASE_URL = "https://azvhzsbreshqospqaybt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6dmh6c2JyZXNocW9zcHFheWJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTIxOTUsImV4cCI6MjA4MjQyODE5NX0.KkbkDVwRkY0iF9gEuiT0FGl5R4YV7Ee5fnZHd0_VfbY"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# ========================================
# HELPER FUNCTIONS
# ========================================

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def register_user(username: str, email: str, password: str):
    """Register a new user in Supabase"""
    try:
        # Check if username exists
        response = supabase.table('users').select('*').eq('username', username).execute()
        if response.data:
            return False, "Username already exists!"
        
        # Check if email exists
        response = supabase.table('users').select('*').eq('email', email).execute()
        if response.data:
            return False, "Email already registered!"
        
        # Create user
        user_data = {
            'username': username,
            'email': email,
            'password': hash_password(password),
            'created_at': datetime.now().isoformat()
        }
        
        supabase.table('users').insert(user_data).execute()
        return True, "Account created successfully!"
        
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(username: str, password: str):
    """Authenticate user login"""
    try:
        response = supabase.table('users').select('*').eq('username', username).execute()
        
        if not response.data:
            return False, "Username not found!", None
        
        user = response.data[0]
        
        if user['password'] == hash_password(password):
            return True, "Login successful!", user['id']
        else:
            return False, "Incorrect password!", None
            
    except Exception as e:
        return False, f"Error: {str(e)}", None

def create_chat_conversation(user_id: int, title: str = "New Chat"):
    """Create a new chat conversation"""
    try:
        chat_data = {
            'user_id': user_id,
            'title': title,
            'created_at': datetime.now().isoformat()
        }
        
        response = supabase.table('conversations').insert(chat_data).execute()
        return response.data[0]['id']
        
    except Exception as e:
        st.error(f"Error creating conversation: {str(e)}")
        return None

def get_user_conversations(user_id: int):
    """Get all conversations for a user"""
    try:
        response = supabase.table('conversations').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading conversations: {str(e)}")
        return []

def save_message(conversation_id: int, role: str, content: str):
    """Save a message to a conversation"""
    try:
        message_data = {
            'conversation_id': conversation_id,
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        supabase.table('messages').insert(message_data).execute()
        
    except Exception as e:
        st.error(f"Error saving message: {str(e)}")

def get_conversation_messages(conversation_id: int):
    """Get all messages in a conversation"""
    try:
        response = supabase.table('messages').select('*').eq('conversation_id', conversation_id).order('timestamp', desc=False).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading messages: {str(e)}")
        return []

def update_conversation_title(conversation_id: int, title: str):
    """Update conversation title"""
    try:
        supabase.table('conversations').update({'title': title}).eq('id', conversation_id).execute()
    except Exception as e:
        st.error(f"Error updating title: {str(e)}")

def generate_chat_title(first_message: str) -> str:
    """Generate a short title from the first message"""
    # Take first 5 words or 40 characters, whichever is shorter
    words = first_message.split()[:5]
    title = ' '.join(words)
    if len(title) > 40:
        title = title[:37] + "..."
    return title

def delete_conversation(conversation_id: int):
    """Delete a conversation and all its messages"""
    try:
        # Delete messages first
        supabase.table('messages').delete().eq('conversation_id', conversation_id).execute()
        # Delete conversation
        supabase.table('conversations').delete().eq('id', conversation_id).execute()
    except Exception as e:
        st.error(f"Error deleting conversation: {str(e)}")

# ========================================
# PAGE CONFIGURATION
# ========================================

st.set_page_config(
    page_title="DavBel AI",
    page_icon="✖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CUSTOM CSS - GEMINI-STYLE UI
# ========================================

st.markdown("""
    <style>
    /* Main App Styling */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    
    /* Logo Styling */
    .logo-container {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 20px;
    }
    
    .logo {
        font-size: 80px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }
    
    .app-title {
        font-size: 36px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 10px;
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Input Fields */
    .stTextInput>div>div>input {
        background-color: #1e1e2f;
        border: 2px solid #667eea;
        border-radius: 12px;
        color: white;
        padding: 12px;
        font-size: 16px;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 16px 20px;
        border-radius: 18px;
        margin: 10px 0;
        animation: slideIn 0.3s ease;
        max-width: 85%;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin-left: auto;
        margin-right: 0;
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #2d2d3f 0%, #1e1e2f 100%);
        margin-right: auto;
        margin-left: 0;
        border: 1px solid #667eea;
        color: white;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0a0e27 100%);
    }
    
    /* Conversation List */
    .conversation-item {
        padding: 12px;
        margin: 5px 0;
        background: #1e1e2f;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .conversation-item:hover {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border: 1px solid #667eea;
        transform: translateX(5px);
    }
    
    .conversation-item-active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: 1px solid #764ba2;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Welcome Screen */
    .welcome-card {
        background: linear-gradient(135deg, #2d2d3f 0%, #1e1e2f 100%);
        border: 2px solid #667eea;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        margin: 20px auto;
        max-width: 600px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    /* Info Cards */
    .info-card {
        background: linear-gradient(135deg, #2d2d3f 0%, #1e1e2f 100%);
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ========================================
# SESSION STATE INITIALIZATION
# ========================================

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'chat_model' not in st.session_state:
    st.session_state.chat_model = None
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

# ========================================
# LOGIN PAGE
# ========================================

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and Title
        st.markdown("""
            <div class='logo-container'>
                <div class='logo'>✖️</div>
                <div class='app-title'>DavBel AI</div>
                <p style='color: rgba(255,255,255,0.8); margin-top: 10px;'>Your Intelligent Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; margin-top: 30px;'>Welcome Back!</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("🚀 Login", use_container_width=True):
                if username and password:
                    success, message, user_id = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_id = user_id
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields!")
        
        with col_b:
            if st.button("📝 Sign Up", use_container_width=True):
                st.session_state.page = 'signup'
                st.rerun()

# ========================================
# SIGNUP PAGE
# ========================================

def show_signup_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and Title
        st.markdown("""
            <div class='logo-container'>
                <div class='logo'>✖️</div>
                <div class='app-title'>DavBel AI</div>
                <p style='color: rgba(255,255,255,0.8); margin-top: 10px;'>Join the Future of AI</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; margin-top: 30px;'>Create Your Account</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("👤 Username", placeholder="Choose a unique username", key="signup_username")
        email = st.text_input("📧 Email", placeholder="your.email@example.com", key="signup_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Choose a strong password", key="signup_password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password", key="signup_confirm")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("✨ Create Account", use_container_width=True):
                if username and email and password and confirm_password:
                    if not validate_email(email):
                        st.error("Invalid email format!")
                    elif password != confirm_password:
                        st.error("Passwords don't match!")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters!")
                    elif len(username) < 3:
                        st.error("Username must be at least 3 characters!")
                    else:
                        success, message = register_user(username, email, password)
                        if success:
                            st.success(message)
                            st.info("✅ You can now login with your credentials!")
                            st.balloons()
                            st.session_state.page = 'login'
                            st.rerun()
                        else:
                            st.error(message)
                else:
                    st.warning("Please fill in all fields!")
        
        with col_b:
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()

# ========================================
# CHAT PAGE
# ========================================

def show_chat_page():
    # Initialize AI model
    if st.session_state.chat_model is None:
        try:
            st.session_state.chat_model = genai.GenerativeModel('models/gemini-2.5-flash')
        except Exception as e:
            st.error(f"Error initializing AI: {str(e)}")
            return
    
    # Sidebar
    with st.sidebar:
        # Logo in sidebar
        st.markdown("""
            <div style='text-align: center; padding: 20px;'>
                <div style='font-size: 50px;'>✖️</div>
                <h2 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          -webkit-background-clip: text;
                          -webkit-text-fill-color: transparent;'>
                    DavBel AI
                </h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div class='info-card'><strong>👤 {st.session_state.username}</strong></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # New Chat Button
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.session_state.chat_session = None
            st.rerun()
        
        st.markdown("### 💬 Your Conversations")
        
        # Load conversations
        conversations = get_user_conversations(st.session_state.user_id)
        
        if conversations:
            for conv in conversations:
                is_active = conv['id'] == st.session_state.current_conversation_id
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    if st.button(
                        f"{'📍' if is_active else '💭'} {conv['title'][:30]}...",
                        key=f"conv_{conv['id']}",
                        use_container_width=True
                    ):
                        st.session_state.current_conversation_id = conv['id']
                        st.session_state.chat_session = None
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv['id']}", help="Delete conversation"):
                        delete_conversation(conv['id'])
                        if st.session_state.current_conversation_id == conv['id']:
                            st.session_state.current_conversation_id = None
                            st.session_state.chat_session = None
                        st.rerun()
        else:
            st.info("No conversations yet. Start a new chat!")
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main chat area
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;'>
                Chat with DavBel AI ✖️
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Display messages or welcome screen
    if st.session_state.current_conversation_id:
        messages = get_conversation_messages(st.session_state.current_conversation_id)
        
        # Display messages
        for msg in messages:
            if msg['role'] == 'user':
                st.markdown(f"""
                    <div class='chat-message user-message'>
                        <strong>You</strong><br>
                        {msg['content']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='chat-message assistant-message'>
                        <strong>✖️ DavBel AI</strong><br>
                        {msg['content']}
                    </div>
                """, unsafe_allow_html=True)
    else:
        # Welcome screen
        st.markdown("""
            <div class='welcome-card'>
                <div style='font-size: 60px; margin-bottom: 20px;'>✖️</div>
                <h2>Welcome to DavBel AI!</h2>
                <p style='font-size: 18px; color: rgba(255,255,255,0.7); margin-top: 20px;'>
                    I'm here to help you with anything you need. Ask me questions, get creative ideas,
                    solve problems, or just have a conversation!
                </p>
                <p style='margin-top: 30px; color: #667eea;'>
                    💡 Start by typing a message below
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Create new conversation if needed
        if not st.session_state.current_conversation_id:
            title = generate_chat_title(user_input)
            conv_id = create_chat_conversation(st.session_state.user_id, title)
            st.session_state.current_conversation_id = conv_id
        
        # Initialize chat session if needed
        if st.session_state.chat_session is None:
            # Load previous messages for context
            messages = get_conversation_messages(st.session_state.current_conversation_id)
            history = []
            for msg in messages:
                history.append({
                    "role": msg['role'],
                    "parts": [msg['content']]
                })
            
            st.session_state.chat_session = st.session_state.chat_model.start_chat(history=history)
        
        # Save user message
        save_message(st.session_state.current_conversation_id, "user", user_input)
        
        # Get AI response
        try:
            response = st.session_state.chat_session.send_message(user_input)
            ai_response = response.text
            
            # Save AI response
            save_message(st.session_state.current_conversation_id, "model", ai_response)
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ========================================
# MAIN APP
# ========================================

def main():
    if not st.session_state.logged_in:
        if st.session_state.page == 'login':
            show_login_page()
        elif st.session_state.page == 'signup':
            show_signup_page()
    else:
        show_chat_page()

if __name__ == "__main__":
    main()