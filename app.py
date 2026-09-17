import html
import os
import re
import secrets
from datetime import datetime, timezone

import streamlit as st

try:
    from supabase import create_client
except ImportError:
    create_client = None

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

st.set_page_config(page_title="Friend Gup Shup", page_icon="💬", layout="centered", initial_sidebar_state="collapsed")


def secret(name: str) -> str:
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return str(value or os.getenv(name, "")).strip()


def client():
    if create_client is None:
        return None
    url = secret("SUPABASE_URL")
    key = secret("SUPABASE_KEY") or secret("SUPABASE_PUBLISHABLE_KEY") or secret("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def require_client():
    c = client()
    if c is None:
        raise RuntimeError("Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Cloud → Manage app → Settings → Secrets.")
    return c


def clean_name(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())[:40]


def new_code() -> str:
    return secrets.token_hex(4).upper()


def get_profile(code: str):
    try:
        return require_client().table("users").select("id,friend_id,name,created_at").eq("friend_id", code).maybe_single().execute().data
    except Exception:
        return None


def create_profile(name: str):
    name = clean_name(name) or "Friend"
    c = require_client()
    for _ in range(8):
        code = new_code()
        try:
            result = c.table("users").insert({"friend_id": code, "name": name}).execute()
            return (result.data or [None])[0]
        except Exception as e:
            if "duplicate" not in str(e).lower() and "unique" not in str(e).lower():
                raise
    raise RuntimeError("Could not create a Friend Code. Please try again.")


def update_profile(db_id, name):
    result = require_client().table("users").update({"name": clean_name(name) or "Friend"}).eq("id", db_id).execute()
    return (result.data or [None])[0]


def user_by_code(code: str):
    code = (code or "").strip().upper()
    if not code:
        return None
    try:
        return require_client().table("users").select("id,friend_id,name").eq("friend_id", code).maybe_single().execute().data
    except Exception:
        return None


def get_friends(my_db_id):
    try:
        c = require_client()
        links = c.table("friendships").select("friend_id,created_at").eq("user_id", my_db_id).order("created_at").execute().data or []
        if not links:
            return []
        ids = [str(row["friend_id"]) for row in links]
        users = c.table("users").select("id,friend_id,name").in_("id", ids).execute().data or []
        by_id = {str(row["id"]): row for row in users}
        return [
            {"db_id": row["friend_id"], "code": by_id[str(row["friend_id"])]["friend_id"], "name": by_id[str(row["friend_id"])]["name"]}
            for row in links if str(row["friend_id"]) in by_id
        ]
    except Exception as e:
        st.error(f"Could not load friends: {e}")
        return []


def add_friend(my_db_id, code):
    friend = user_by_code(code)
    if not friend:
        return False, "That Friend Code was not found. Ask your friend to copy their code again."
    if int(friend["id"]) == int(my_db_id):
        return False, "That is your own Friend Code."
    try:
        c = require_client()
        c.table("friendships").upsert({"user_id": my_db_id, "friend_id": friend["id"]}, on_conflict="user_id,friend_id").execute()
        c.table("friendships").upsert({"user_id": friend["id"], "friend_id": my_db_id}, on_conflict="user_id,friend_id").execute()
        return True, friend
    except Exception as e:
        return False, str(e)


def get_messages(my_code, friend_code):
    try:
        c = require_client()
        query = f"and(sender_id.eq.{my_code},receiver_id.eq.{friend_code}),and(sender_id.eq.{friend_code},receiver_id.eq.{my_code})"
        return c.table("messages").select("id,sender_id,receiver_id,message,created_at").or_(query).order("created_at").execute().data or []
    except Exception as e:
        st.error(f"Could not load messages: {e}")
        return []


def send_message(my_code, friend_code, text):
    text = (text or "").strip()
    if not text:
        return False, "Write a message first."
    if len(text) > 2000:
        return False, "Message is too long."
    try:
        require_client().table("messages").insert({
            "sender_id": my_code,
            "receiver_id": friend_code,
            "message": text,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return True, ""
    except Exception as e:
        return False, str(e)


st.markdown("""
<style>
#MainMenu, footer {visibility:hidden;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stAppViewContainer"] {background:linear-gradient(180deg,#fff8fc 0%,#f7f7ff 100%);}
.block-container {max-width:760px;padding:14px 12px 80px;}
.hero {padding:22px 16px;border-radius:26px;background:linear-gradient(135deg,#ffdbea,#e7ddff);text-align:center;margin-bottom:14px;box-shadow:0 8px 25px rgba(90,60,100,.08);}
.hero h1 {margin:0;color:#292235;font-size:30px;font-weight:850;}
.hero p {margin:6px 0 0;color:#5b5062;font-size:14px;}
.card {padding:16px;border-radius:20px;background:rgba(255,255,255,.9);border:1px solid #eee2ea;box-shadow:0 5px 16px rgba(70,50,80,.05);margin-bottom:12px;}
.codebox {padding:12px;border-radius:15px;background:#faf7ff;border:1px dashed #bda7d0;text-align:center;font-size:24px;letter-spacing:3px;font-weight:850;}
.chatbox {height:56vh;min-height:360px;overflow-y:auto;padding:12px;border-radius:20px;background:rgba(255,255,255,.82);border:1px solid #eadfe8;}
.bubble {padding:10px 13px;border-radius:18px;margin:8px 0;max-width:82%;word-break:break-word;line-height:1.45;}
.me {background:#ffd9e8;margin-left:auto;border-bottom-right-radius:5px;}
.friend {background:#f0eff5;margin-right:auto;border-bottom-left-radius:5px;}
.meta {font-size:10px;color:#756b78;margin-top:3px;}
.small {font-size:12px;color:#756b78;}
.friend-card {padding:4px 0;}
.stButton > button {border-radius:14px;font-weight:700;min-height:46px;}
[data-testid="stTextInput"] input {border-radius:14px;}
@media(max-width:600px){.hero h1{font-size:27px}.chatbox{height:58vh;min-height:320px}.bubble{max-width:90%}.block-container{padding-left:9px;padding-right:9px;}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>💬 Friend Gup Shup</h1><p>Simple private friend-to-friend chat</p></div>', unsafe_allow_html=True)

if st_autorefresh:
    st_autorefresh(interval=2500, key="messages_refresh")

if create_client is None or not secret("SUPABASE_URL") or not (secret("SUPABASE_KEY") or secret("SUPABASE_PUBLISHABLE_KEY") or secret("SUPABASE_ANON_KEY")):
    st.error("Supabase connection is missing. Add your Supabase URL and publishable key in Streamlit Secrets.")
    st.stop()

# Restore identity from the URL after a browser refresh.
url_code = str(st.query_params.get("friend", "")).strip().upper()
if url_code and not st.session_state.get("profile_ready"):
    p = get_profile(url_code)
    if p:
        st.session_state.update(profile_ready=True, user_db_id=p["id"], friend_code=p["friend_id"], display_name=p["name"])

if not st.session_state.get("profile_ready"):
    st.markdown('<div class="card"><h3 style="margin-top:0">👋 First time here?</h3><p>Enter your name once. We will create your Friend Code.</p></div>', unsafe_allow_html=True)
    name = st.text_input("Your name", placeholder="Your name", max_chars=40)
    if st.button("Start chatting 💕", type="primary", use_container_width=True):
        if not clean_name(name):
            st.warning("Please enter your name.")
        else:
            try:
                p = create_profile(name)
                st.session_state.update(profile_ready=True, user_db_id=p["id"], friend_code=p["friend_id"], display_name=p["name"])
                st.query_params["friend"] = p["friend_id"]
                st.rerun()
            except Exception as e:
                st.error(str(e))
    st.stop()

my_db_id = st.session_state.user_db_id
my_code = st.session_state.friend_code
my_name = st.session_state.display_name

friends = get_friends(my_db_id)

# Top actions: only two things the user normally needs.
a, b = st.columns(2)
with a:
    if st.button("👤 My code", use_container_width=True):
        st.session_state.page = "code"
with b:
    if st.button("➕ Add friend", use_container_width=True):
        st.session_state.page = "add"

page = st.session_state.get("page", "chat")

if page == "code":
    st.markdown('<div class="card"><h3 style="margin-top:0">👤 Your Friend Code</h3><p class="small">Send this 8-character code to your friend. They enter it once.</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="codebox">{html.escape(my_code)}</div>', unsafe_allow_html=True)
    st.code(my_code, language=None)
    st.caption("Use the copy icon on the code box above to copy your Friend Code.")
    with st.expander("✏️ Change my name"):
        new_name_value = st.text_input("Name", value=my_name, max_chars=40)
        if st.button("Save name", use_container_width=True):
            try:
                p = update_profile(my_db_id, new_name_value)
                st.session_state.display_name = p["name"]
                st.success("Name updated.")
                st.rerun()
            except Exception as e:
                st.error(str(e))
    if st.button("← Back to chat", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()
    st.stop()

if page == "add":
    st.markdown('<div class="card"><h3 style="margin-top:0">➕ Add your friend</h3><p class="small">Ask your friend for their 8-character Friend Code, enter it below, and the chat opens automatically.</p></div>', unsafe_allow_html=True)
    code = st.text_input("Friend Code", placeholder="e.g. BC9FABE6", max_chars=8).strip().upper()
    if st.button("Connect & open chat 🤝", type="primary", use_container_width=True):
        ok, result = add_friend(my_db_id, code)
        if ok:
            st.session_state.selected_friend = result["friend_id"]
            st.session_state.page = "chat"
            st.success(f"Connected with {result['name']}!")
            st.rerun()
        else:
            st.error(result)
    if st.button("← Back", use_container_width=True):
        st.session_state.page = "chat"
        st.rerun()
    st.stop()

# CHAT PAGE
if not friends:
    st.markdown('<div class="card"><h3 style="margin-top:0">💬 No friends yet</h3><p>Tap <b>➕ Add friend</b>, enter your friend’s code, and you will go straight to the chat.</p></div>', unsafe_allow_html=True)
    st.stop()

friend_codes = [f["code"] for f in friends]
selected_code = st.session_state.get("selected_friend")
if selected_code not in friend_codes:
    selected_code = friend_codes[0]
    st.session_state.selected_friend = selected_code

# Friend buttons instead of a dropdown.
if len(friends) == 1:
    selected = friends[0]
else:
    st.caption("Your friends")
    cols = st.columns(min(3, len(friends)))
    for i, f in enumerate(friends):
        with cols[i % len(cols)]:
            label = ("🟣 " if f["code"] == selected_code else "") + f["name"]
            if st.button(label, key=f"friend_{f['code']}", use_container_width=True):
                st.session_state.selected_friend = f["code"]
                st.rerun()
    selected = next(f for f in friends if f["code"] == selected_code)

friend_code = selected["code"]
friend_name = selected["name"]

st.markdown(f'<div class="card"><h3 style="margin:0">🟢 {html.escape(friend_name)}</h3><div class="small">Messages refresh automatically</div></div>', unsafe_allow_html=True)

messages = get_messages(my_code, friend_code)
chat_html = '<div class="chatbox">'
if not messages:
    chat_html += '<p style="text-align:center;color:#888;margin-top:25vh">No messages yet.<br>Say hello 👋</p>'
for m in messages:
    mine = m["sender_id"] == my_code
    cls = "me" if mine else "friend"
    who = "You" if mine else friend_name
    try:
        dt = datetime.fromisoformat(str(m["created_at"]).replace("Z", "+00:00"))
        time_text = dt.astimezone().strftime("%I:%M %p")
    except Exception:
        time_text = ""
    safe_text = html.escape(str(m["message"])).replace("\n", "<br>")
    chat_html += f'<div class="bubble {cls}"><b>{html.escape(who)}</b><br>{safe_text}<div class="meta">{time_text}</div></div>'
chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

with st.form("message_form", clear_on_submit=True, border=False):
    text = st.text_input("Message", placeholder=f"Message {friend_name}…", label_visibility="collapsed", max_chars=2000)
    send = st.form_submit_button("Send 💕", type="primary", use_container_width=True)
    if send:
        ok, error = send_message(my_code, friend_code, text)
        if not ok:
            st.error(error)
        else:
            st.rerun()
