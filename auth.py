from typing import Optional
from models import User, get_db
from sqlalchemy.orm import Session
import streamlit as st

def create_user(email: str, username: str, password: str, db: Session) -> Optional[User]:
    """Create a new user"""
    # Check if user already exists
    if db.query(User).filter(User.email == email).first():
        return None
    
    # Create new user
    hashed_password = User.hash_password(password)
    user = User(
        email=email,
        username=username,
        password_hash=hashed_password
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user"""
    user = db.query(User).filter(User.username == username).first()
    if user and user.verify_password(password):
        return user
    return None

def init_session_state():
    """Initialize session state for authentication"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

def login_user(user: User):
    """Log in a user"""
    st.session_state.user = user
    st.session_state.is_authenticated = True
    st.session_state.instance_id = user.instance_id
    st.session_state.client_id = user.client_id

def logout_user():
    """Log out the current user"""
    st.session_state.user = None
    st.session_state.is_authenticated = False
    st.session_state.instance_id = ''
    st.session_state.client_id = ''
