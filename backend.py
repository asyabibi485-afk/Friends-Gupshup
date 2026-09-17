import os
import uuid
from datetime import datetime, timezone
import streamlit as st

try:
    from supabase import create_client
except ImportError:
    create_client = None

def _client():
    if create_client is None:
        return None
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))
    if not url or not key:
        return None
    return create_client(url, key)

def _require():
    client = _client()
    if client is None:
        raise RuntimeError("Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets.")
    return client

def get_or_create_user():
    if "real_chat_user_id" not in st.session_state:
        st.session_state.real_chat_user_id = str(uuid.uuid4())
    return st.session_state.real_chat_user_id

def get_friends(user_id):
    try:
        c = _require()
        res = c.table("friendships").select("friend_id,friend_name").eq("user_id", user_id).execute()
        return [{"friend_id": x["friend_id"], "name": x["friend_name"]} for x in (res.data or [])]
    except Exception as e:
        st.error(str(e))
        return []

def add_friend(user_id, friend_id, friend_name):
    if not friend_id or not friend_name:
        return False, "Enter both Friend ID and name."
    if friend_id == user_id:
        return False, "You cannot add yourself."
    try:
        c = _require()
        c.table("friendships").upsert(
            {"user_id": user_id, "friend_id": friend_id, "friend_name": friend_name},
            on_conflict="user_id,friend_id"
        ).execute()
        return True, "Friend added."
    except Exception as e:
        return False, str(e)

def get_messages(user_id, friend_id):
    try:
        c = _require()
        r1 = c.table("messages").select("*").eq("sender_id", user_id).eq("receiver_id", friend_id).execute()
        r2 = c.table("messages").select("*").eq("sender_id", friend_id).eq("receiver_id", user_id).execute()
        data = (r1.data or []) + (r2.data or [])
        return sorted(data, key=lambda x: x.get("created_at", ""))
    except Exception as e:
        st.error(str(e))
        return []

def send_message(sender_id, receiver_id, message):
    try:
        c = _require()
        c.table("messages").insert({
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": message,
            "created_at": datetime.now(timezone.utc).isoformat()
        }).execute()
        return True, "Sent"
    except Exception as e:
        return False, str(e)
