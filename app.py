import streamlit as st
from datetime import datetime, timezone
from backend import get_friends, get_messages, send_message, add_friend, get_or_create_user
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Friend Gup Shup 💬", page_icon="💬", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background:#fff8fb;}
.hero{padding:22px;border-radius:24px;background:linear-gradient(135deg,#ffdce9,#e8ddff);
text-align:center;margin-bottom:18px;}
.hero h1{margin:0;font-size:38px;}
.chatbox{height:55vh;overflow-y:auto;padding:12px;border-radius:20px;background:#fff;
border:1px solid #efdce6;}
.bubble{padding:11px 15px;border-radius:18px;margin:8px 0;max-width:75%;word-wrap:break-word;}
.me{background:#ffd9e8;margin-left:auto;}
.friend{background:#f0eff4;margin-right:auto;}
.meta{font-size:11px;color:#777;margin-top:4px;}
.friend-card{padding:14px;border:1px solid #eadce4;border-radius:16px;background:white;margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

if "user_id" not in st.session_state:
    st.session_state.user_id = get_or_create_user()
if "selected_friend" not in st.session_state:
    st.session_state.selected_friend = None

# Refresh every 2 seconds so messages sent by another user appear automatically.
st_autorefresh(interval=2000, key="chat_refresh")

st.markdown("""
<div class="hero">
<h1>💬 Friend Gup Shup</h1>
<p>Real friend-to-friend chat • No AI replies</p>
</div>
""", unsafe_allow_html=True)

friends = get_friends(st.session_state.user_id)

with st.sidebar:
    st.header("👭 Friends")
    if not friends:
        st.info("Add a friend using their Friend ID.")
    for f in friends:
        label = f"{f['name']}  •  {f['friend_id'][:8]}"
        if st.button(label, key=f"friend_{f['friend_id']}", use_container_width=True):
            st.session_state.selected_friend = f["friend_id"]
            st.rerun()

    st.divider()
    st.caption("Your Friend ID")
    st.code(st.session_state.user_id[:12])

    with st.expander("➕ Add friend"):
        friend_id = st.text_input("Friend ID")
        friend_name = st.text_input("Friend name")
        if st.button("Add Friend", use_container_width=True):
            ok, message = add_friend(st.session_state.user_id, friend_id.strip(), friend_name.strip())
            if ok:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

if not st.session_state.selected_friend:
    st.info("👈 Select a friend to start a real chat. Both people must use the same Supabase database.")
    st.markdown("""
### How real chat works
1. You share your **Friend ID** with your friend.
2. Your friend adds your ID.
3. When either person sends a message, it is saved to the shared database.
4. The chat automatically refreshes every 2 seconds.
5. There are **no AI-generated replies**.
""")
    st.stop()

selected = next((f for f in friends if f["friend_id"] == st.session_state.selected_friend), None)
friend_name = selected["name"] if selected else "Friend"

st.subheader(f"🟢 {friend_name}")
st.caption("Real person-to-person conversation")

messages = get_messages(st.session_state.user_id, st.session_state.selected_friend)

chat_html = '<div class="chatbox">'
for m in messages:
    mine = m["sender_id"] == st.session_state.user_id
    cls = "me" if mine else "friend"
    who = "You" if mine else friend_name
    try:
        dt = datetime.fromisoformat(m["created_at"].replace("Z", "+00:00"))
        time_text = dt.astimezone().strftime("%d %b, %I:%M %p")
    except Exception:
        time_text = ""
    safe_text = str(m["message"]).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    chat_html += f'<div class="bubble {cls}"><b>{who}</b><br>{safe_text}<div class="meta">{time_text}</div></div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

with st.form("send_message", clear_on_submit=True):
    col1, col2 = st.columns([5,1])
    with col1:
        text = st.text_input("Write a message…", label_visibility="collapsed", placeholder="Type your message")
    with col2:
        send = st.form_submit_button("Send 💕", use_container_width=True)
    if send and text.strip():
        ok, message = send_message(st.session_state.user_id, st.session_state.selected_friend, text.strip())
        if not ok:
            st.error(message)
        else:
            st.rerun()
