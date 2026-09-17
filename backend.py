import os
import re
import uuid
from datetime import datetime, timezone
import streamlit as st

try:
    from supabase import create_client
except ImportError:
    create_client = None


def _secret(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.getenv(name, "")).strip()


def _client():
    if create_client is None:
        return None
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def configuration_error():
    if create_client is None:
        return "Supabase Python package is not installed. Redeploy after installing requirements.txt."
    if not _secret("SUPABASE_URL") or not _secret("SUPABASE_KEY"):
        return "Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets."
    return ""


def _require():
    c = _client()
    if c is None:
        raise RuntimeError(configuration_error() or "Supabase connection is unavailable.")
    return c


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip())[:40]


def get_or_create_user():
    """Keep the demo identity in the Streamlit session. Users can restore it later with the full ID."""
    if "real_chat_user_id" not in st.session_state:
        st.session_state.real_chat_user_id = str(uuid.uuid4())
    return st.session_state.real_chat_user_id


def get_user(user_id):
    try:
        c = _require()
        res = c.table("users").select("id,display_name,friend_code,created_at").eq("id", user_id).maybe_single().execute()
        return res.data
    except Exception:
        return None


def ensure_user(user_id, display_name):
    display_name = normalize_name(display_name) or "Friend"
    try:
        c = _require()
        existing = get_user(user_id)
        if existing:
            if existing.get("display_name") != display_name:
                c.table("users").update({"display_name": display_name}).eq("id", user_id).execute()
                existing["display_name"] = display_name
            return existing
        friend_code = uuid.uuid4().hex[:8].upper()
        res = c.table("users").insert({"id": user_id, "display_name": display_name, "friend_code": friend_code}).execute()
        return (res.data or [None])[0]
    except Exception as e:
        raise RuntimeError(str(e))


def get_user_by_friend_code(friend_code):
    code = (friend_code or "").strip().upper()
    if not code:
        return None
    try:
        c = _require()
        res = c.table("users").select("id,display_name,friend_code").eq("friend_code", code).maybe_single().execute()
        return res.data
    except Exception:
        return None


def get_friends(user_id):
    try:
        c = _require()
        res = (
            c.table("friendships")
            .select("friend_id,friend_name")
            .eq("user_id", user_id)
            .order("created_at")
            .execute()
        )
        return [{"friend_id": x["friend_id"], "name": x["friend_name"]} for x in (res.data or [])]
    except Exception as e:
        st.error(str(e))
        return []


def add_friend(user_id, friend_code):
    friend = get_user_by_friend_code(friend_code)
    if not friend:
        return False, "No user found with that Friend Code. Ask your friend to share the 8-character code."
    if friend["id"] == user_id:
        return False, "You cannot add yourself."
    try:
        c = _require()
        # Create both directions so either person immediately sees the chat.
        c.table("friendships").upsert(
            {"user_id": user_id, "friend_id": friend["id"], "friend_name": friend["display_name"]},
            on_conflict="user_id,friend_id",
        ).execute()
        me = get_user(user_id)
        my_name = (me or {}).get("display_name", "Friend")
        c.table("friendships").upsert(
            {"user_id": friend["id"], "friend_id": user_id, "friend_name": my_name},
            on_conflict="user_id,friend_id",
        ).execute()
        return True, f"Connected with {friend['display_name']}!"
    except Exception as e:
        return False, str(e)


def get_messages(user_id, friend_id):
    try:
        c = _require()
        # One query is simpler and avoids missing messages if the app reruns rapidly.
        r = (
            c.table("messages")
            .select("id,sender_id,receiver_id,message,created_at")
            .or_(f"and(sender_id.eq.{user_id},receiver_id.eq.{friend_id}),and(sender_id.eq.{friend_id},receiver_id.eq.{user_id})")
            .order("created_at")
            .execute()
        )
        return r.data or []
    except Exception as e:
        st.error(str(e))
        return []


def send_message(sender_id, receiver_id, message):
    text = (message or "").strip()
    if not text:
        return False, "Message cannot be empty."
    if len(text) > 2000:
        return False, "Message is too long (maximum 2,000 characters)."
    try:
        c = _require()
        c.table("messages").insert({
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": text,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return True, "Sent"
    except Exception as e:
        return False, str(e)
