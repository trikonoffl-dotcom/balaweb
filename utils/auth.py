import streamlit as st
import hashlib
from utils.db import get_supabase

def hash_password(password: str) -> str:
    """Simple SHA-256 hashing for demonstration."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(email: str, password: str):
    """Verifies user credentials against Supabase."""
    try:
        supabase = get_supabase()
        pwd_hash = hash_password(password)
        
        response = supabase.table("users").select("*").eq("email", email).eq("password_hash", pwd_hash).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            st.session_state["logged_in"] = True
            st.session_state["user"] = {
                "id": user["id"],
                "email": user["email"],
                "role": user["role"],
                "allowed_tools": user.get("allowed_tools", ["Dashboard"])
            }
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def logout():
    """Clears the session state."""
    if "logged_in" in st.session_state:
        del st.session_state["logged_in"]
    if "user" in st.session_state:
        del st.session_state["user"]
    st.rerun()

def get_current_user():
    """Returns the current user from session state."""
    return st.session_state.get("user")

def is_logged_in():
    """Checks if a user is logged in."""
    return st.session_state.get("logged_in", False)
