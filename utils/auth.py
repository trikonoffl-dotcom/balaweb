import streamlit as st
import hashlib
import extra_streamlit_components as stx
from utils.db import get_supabase
import time
import datetime

# --- COOKIE MANAGER SETUP ---
@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

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
            # Set Session
            _set_user_session(user)
            # Set Cookie (Expires in 7 days)
            cookie_manager.set("trikon_auth_token", user["id"], expires_at=datetime.datetime.now() + datetime.timedelta(days=7))
            return True
        return False
    except Exception as e:
        st.error(f"Login failed: {e}")
        return False

def _set_user_session(user):
    """Wait - helper to set session state."""
    st.session_state["logged_in"] = True
    st.session_state["user"] = {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "allowed_tools": user.get("allowed_tools", ["Dashboard"])
    }

def logout():
    """Clears the session state and cookie."""
    cookie_manager.delete("trikon_auth_token")
    if "logged_in" in st.session_state:
        del st.session_state["logged_in"]
    if "user" in st.session_state:
        del st.session_state["user"]
    st.rerun()

def get_current_user():
    """Returns the current user from session state."""
    return st.session_state.get("user")

def is_logged_in():
    """Checks if a user is logged in, restoring from cookie if needed."""
    if st.session_state.get("logged_in", False):
        return True
    
    # Try restoring from cookie
    try:
        user_id = cookie_manager.get(cookie="trikon_auth_token")
        if user_id:
            # Validate ID against DB (Prevents fake cookies)
            supabase = get_supabase()
            response = supabase.table("users").select("*").eq("id", user_id).execute()
            if response.data:
                _set_user_session(response.data[0])
                time.sleep(0.1) # Small delay to ensure state prop
                return True
    except Exception as e:
        pass # Cookie read failed or invalid

    return False
