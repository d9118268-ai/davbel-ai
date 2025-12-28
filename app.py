# ========================================
# DAVBEL AI - GROQ POWERED + MOBILE OPTIMIZED
# No limits, Real app feel!
# ========================================

# REQUIREMENTS (update requirements.txt):
# streamlit==1.52.2
# groq==0.11.0
# supabase==2.27.0

import streamlit as st
from groq import Groq
from supabase import create_client, Client
from datetime import datetime
import hashlib
import re

# ========================================
# CONFIGURATION
# ========================================

# Groq API Key (FREE UNLIMITED!)
GROQ_API_KEY = "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"  # Replace with your Groq API key

# Supabase Configuration
SUPABASE_URL = "https://azvhzsbreshqospqaybt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6dmh6c2JyZXNocW9zcHFheWJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY4NTIxOTUsImV4cCI6MjA4MjQyODE5NX0.KkbkDVwRkY0iF9gEuiT0FGl5R4YV7Ee5fnZHd0_VfbY"

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

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
        response = supabase.table('users').select('*').eq('username', username).execute()
        if response.data:
            return False, "Username already exists!"
        
        response = supabase.table('users').select('*').eq('email', email).execute()
        if response.data:
            return False, "Email already registered!"
        
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
    words = first_message.split()[:5]
    title = ' '.join(words)
    if len(title) > 40:
        title = title[:37] + "..."
    return title

def delete_conversation(conversation_id: int):
    """Delete a conversation and all its messages"""
    try:
        supabase.table('messages').delete().eq('conversation_id', conversation_id).execute()
        supabase.table('conversations').delete().eq('id', conversation_id).execute()
    except Exception as e:
        st.error(f"Error deleting conversation: {str(e)}")

def chat_with_groq(messages_history, user_message):
    """Send message to Groq AI and get response"""
    try:
        # Build message format for Groq
        groq_messages = []
        for msg in messages_history:
            groq_messages.append({
                "role": "user" if msg['role'] == 'user' else "assistant",
                "content": msg['content']
            })
        groq_messages.append({"role": "user", "content": user_message})
        
        # Call Groq API
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Fast and smart!
            messages=groq_messages,
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            stream=False
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error: {str(e)}"

# ========================================
# PAGE CONFIGURATION - MOBILE OPTIMIZED
# ========================================

st.set_page_config(
    page_title="DavBel AI",
    page_icon="✖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# MOBILE-OPTIMIZED CSS
# ========================================

st.markdown("""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile-first design */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 100%);
        color: #ffffff;
        padding: 0 !important;
        max-width: 100% !important;
    }
    
    /* Mobile optimized container */
    .block-container {
        padding: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Logo - Mobile friendly */
    .logo-container {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 15px;
    }
    
    .logo {
        font-size: 60px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .app-title {
        font-size: 28px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 5px;
    }
    
    /* Mobile-optimized buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 20px;
        font-weight: 600;
        font-size: 16px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        -webkit-tap-highlight-color: transparent;
    }
    
    .stButton>button:active {
        transform: scale(0.95);
    }
    
    /* Mobile input fields */
    .stTextInput>div>div>input {
        background-color: #1e1e2f;
        border: 2px solid #667eea;
        border-radius: 12px;
        color: white;
        padding: 14px;
        font-size: 16px;
        -webkit-appearance: none;
    }
    
    /* Chat input - mobile optimized */
    .stChatInput>div>div>input {
        background-color: #1e1e2f;
        border: 2px solid #667eea;
        border-radius: 20px;
        color: white;
        padding: 12px 16px;
        font-size: 16px;
    }
    
    /* Chat messages - mobile friendly */
    .chat-message {
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        animation: slideIn 0.3s ease;
        max-width: 85%;
        word-wrap: break-word;
        line-height: 1.5;
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
    
    /* Sidebar - mobile friendly */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0a0e27 100%);
    }
    
    /* Conversation list - touch optimized */
    .conversation-item {
        padding: 12px;
        margin: 5px 0;
        background: #1e1e2f;
        border-radius: 10px;
        transition: all 0.2s ease;
        border: 1px solid transparent;
        -webkit-tap-highlight-color: transparent;
    }
    
    .conversation-item:active {
        transform: scale(0.98);
    }
    
    /* Mobile viewport adjustments */
    @media only screen and (max-width: 768px) {
        .logo {
            font-size: 50px;
        }
        
        .app-title {
            font-size: 24px;
        }
        
        .chat-message {
            max-width: 90%;
            font-size: 15px;
        }
        
        .stButton>button {
            padding: 12px 16px;
            font-size: 15px;
        }
    }
    
    /* Touch-friendly spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Remove default padding on mobile */
    @media (max-width: 640px) {
        .block-container {
            padding: 0.5rem !important;
        }
    }
    
    /* Welcome card - mobile optimized */
    .welcome-card {
        background: linear-gradient(135deg, #2d2d3f 0%, #1e1e2f 100%);
        border: 2px solid #667eea;
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        margin: 20px auto;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    /* Info cards - mobile friendly */
    .info-card {
        background: linear-gradient(135deg, #2d2d3f 0%, #1e1e2f 100%);
        border-left: 4px solid #667eea;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
        font-size: 14px;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
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

# ========================================
# LOGIN PAGE
# ========================================

def show_login_page():
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    
    with col2:
        st.markdown("""
            <div class='logo-container'>
                <div class='logo'>✖️</div>
                <div class='app-title'>DavBel AI</div>
                <p style='color: rgba(255,255,255,0.8); margin-top: 10px; font-size: 14px;'>Your Intelligent Assistant</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; margin-top: 20px; font-size: 24px;'>Welcome Back!</h2>", unsafe_allow_html=True)
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
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    
    with col2:
        st.markdown("""
            <div class='logo-container'>
                <div class='logo'>✖️</div>
                <div class='app-title'>DavBel AI</div>
                <p style='color: rgba(255,255,255,0.8); margin-top: 10px; font-size: 14px;'>Join the Future of AI</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; margin-top: 20px; font-size: 24px;'>Create Account</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        username = st.text_input("👤 Username", placeholder="Choose a username", key="signup_username")
        email = st.text_input("📧 Email", placeholder="your.email@example.com", key="signup_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Choose a password", key="signup_password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter password", key="signup_confirm")
        
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
                            st.info("✅ You can now login!")
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
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 15px;'>
                <div style='font-size: 40px;'>✖️</div>
                <h2 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          -webkit-background-clip: text;
                          -webkit-text-fill-color: transparent;
                          font-size: 22px;'>
                    DavBel AI
                </h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div class='info-card'><strong>👤 {st.session_state.username}</strong></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.current_conversation_id = None
            st.rerun()
        
        st.markdown("### 💬 Chats")
        
        conversations = get_user_conversations(st.session_state.user_id)
        
        if conversations:
            for conv in conversations:
                is_active = conv['id'] == st.session_state.current_conversation_id
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    if st.button(
                        f"{'📍' if is_active else '💭'} {conv['title'][:25]}...",
                        key=f"conv_{conv['id']}",
                        use_container_width=True
                    ):
                        st.session_state.current_conversation_id = conv['id']
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv['id']}"):
                        delete_conversation(conv['id'])
                        if st.session_state.current_conversation_id == conv['id']:
                            st.session_state.current_conversation_id = None
                        st.rerun()
        else:
            st.info("No chats yet!")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main chat area
    st.markdown("""
        <div style='text-align: center; padding: 15px;'>
            <h1 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;
                      font-size: 26px;'>
                Chat with DavBel AI ✖️
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Display messages
    if st.session_state.current_conversation_id:
        messages = get_conversation_messages(st.session_state.current_conversation_id)
        
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
        st.markdown("""
            <div class='welcome-card'>
                <div style='font-size: 50px; margin-bottom: 15px;'>✖️</div>
                <h2 style='font-size: 22px;'>Welcome to DavBel AI!</h2>
                <p style='font-size: 16px; color: rgba(255,255,255,0.7); margin-top: 15px;'>
                    I'm powered by Groq - fast, smart, and unlimited!
                </p>
                <p style='margin-top: 20px; color: #667eea; font-size: 14px;'>
                    💡 Start chatting below
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Type your message...")
    
    if user_input:
        if not st.session_state.current_conversation_id:
            title = generate_chat_title(user_input)
            conv_id = create_chat_conversation(st.session_state.user_id, title)
            st.session_state.current_conversation_id = conv_id
        
        save_message(st.session_state.current_conversation_id, "user", user_input)
        
        try:
            messages = get_conversation_messages(st.session_state.current_conversation_id)
            ai_response = chat_with_groq(messages, user_input)
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