import streamlit as st
from supabase import create_client, Client
import datetime

# Handle secrets locally or in cloud
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def log_generation(tool: str, name: str, metadata: dict = None):
    """Logs a generation event to Supabase."""
    try:
        supabase = get_supabase()
        data = {
            "tool": tool,
            "name": name,
            "metadata": metadata or {}
        }
        supabase.table("generations").insert(data).execute()
    except Exception as e:
        # Don't break the app if logging fails
        print(f"Failed to log to Supabase: {e}")

def get_stats():
    """Fetches generation stats from Supabase."""
    try:
        supabase = get_supabase()
        response = supabase.table("generations").select("*", count="exact").execute()
        return response.data, response.count
    except Exception as e:
        print(f"Failed to fetch stats: {e}")
        return [], 0

def get_monthly_stats():
    """Returns counts grouped by month."""
    data, count = get_stats()
    if not data:
        return {}
    
    stats = {}
    for item in data:
        # Parse created_at "2024-01-29T..."
        date_str = item["created_at"][:7] # YYYY-MM
        stats[date_str] = stats.get(date_str, 0) + 1
    return stats
