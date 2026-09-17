import html
from datetime import datetime
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from backend import (
    configuration_error,
    ensure_user,
    get_friends,
    get_messages,
    get_or_create_user,
    add_friend,
    send_message,
)

st.set_page_config(page_title="Friend Gup Shup", page_icon="💬", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
#MainMenu, footer {visibility:hidden;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stAppViewContainer"] {background:linear-gradient(180deg,#fff8fc 0%,#f8f7ff 100%);}
.block-container {max-width:1000px;padding:18px 18px 100px;}
.hero {padding:24px 20px;border-radius:28px;background:linear-gradient(135deg,#ffdbea,#e8ddff);text-align:center;margin-bottom:16px;box-shadow:0 8px 28px rgba(90,60,100,.08);}
.hero h1 {margin:0;font-size:34px;font-weight:800;color:#292235;}
.hero p {margin:7px 0 0;color:#5b5062;font-size:15px;}
.card {padding:18px;border-radius:22px;background:rgba(255,255,255,.88);border:1px solid #eee2ea;box-shadow:0 5px 18px rgba(70,50,80,.05);margin-bottom:14px;}
.codebox {padding:14px;border-radius:16px;background:#faf7ff;border:1px dashed #bda7d0;text-align:center;font-size:25px;letter-spacing:3px;font-weight:800;}
.chatbox {height:55vh;overflow-y:auto;padding:14px;border-radius:22px;background:rgba(255,255,255,.78);border:1px solid #eadfe8;}
.bubble {padding:11px 14px;border-radius:18px;margin:9px 0;max-width:78%;word-break:break-word;line-height:1.45;}
.me {background:#ffd9e8;margin-left:auto;border-bottom-right-radius:5px;}
.friend {background:#f0eff5;margin-right:auto;border-bottom-left-radius:5px;}
.meta {font-size:10px;color:#756b78;margin-top:4px;}
.small {font-size:12px;color:#756b78;}
@media (max-width:700px){.block-container{padding:10px 10px 80px}.hero h1{font-size:29px}.chatbox{height:58vh}.bubble{max-width:88%}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>💬 Friend Gup Shup</h1><p>Real friend-to-friend chat • No AI replies</p></div>', unsafe_allow_html=True)

# Real-time polling. Supabase remains the shared source of truth for every device.
st_autorefresh(interval=2000, key="chat_refresh")

user_id = get_or_create_user()

config_error = configuration_error()
if config_error:
    st.error(config_error)
    with st.expander("⚙️ Fix the connection on Streamlit Cloud", expanded=True):
        st.markdown("""
**1. Create a Supabase project** and run the included `supabase_schema.sql` in SQL Editor.

**2. Open your Streamlit app → Manage app → Settings → Secrets** and add:
```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
```

**3. Save/reboot the app.** Both you and your friends must use this same Supabase project.

> Keep the Supabase key in Streamlit Secrets, never in GitHub.
""")
    st.stop()

# Identity setup / restore.
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
if "profile_ready" not in st.session_state:
    st.session_state.profile_ready = False

if not st.session_state.profile_ready:
    st.markdown('<div class="card"><h3>👋 Create your chat identity</h3><p>Choose a name. Your app will generate a Friend Code that you can share with friends.</p></div>', unsafe_allow_html=True)
    name = st.text_input("Your name", value=st.session_state.display_name, placeholder="e.g. Ali", max_chars=40)
    if st.button("Create / Continue 💕", type="primary", use_container_width=True):
        if not name.strip():
            st.warning("Please enter your name.")
        else:
            try:
                profile = ensure_user(user_id, name)
                st.session_state.display_name = profile["display_name"]
                st.session_state.friend_code = profile["friend_code"]
                st.session_state.profile_ready = True
                st.rerun()
            except Exception as e:
                st.error(str(e))
    st.stop()

# Existing profile.
try:
    profile = ensure_user(user_id, st.session_state.display_name)
    st.session_state.friend_code = profile["friend_code"]
except Exception as e:
    st.error(str(e)); st.stop()

with st.expander("👤 My profile & Friend Code", expanded=False):
    st.write(f"**{st.session_state.display_name}**")
    st.markdown(f'<div class="codebox">{html.escape(st.session_state.friend_code)}</div>', unsafe_allow_html=True)
    st.caption("Share this 8-character Friend Code with someone you trust. They can use it to connect with you.")
    new_name = st.text_input("Change display name", value=st.session_state.display_name, max_chars=40)
    if st.button("Save name", use_container_width=True):
        try:
            profile = ensure_user(user_id, new_name)
            st.session_state.display_name = profile["display_name"]
            st.success("Name updated.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

friends = get_friends(user_id)

with st.expander("➕ Add a friend", expanded=not friends):
    code = st.text_input("Friend Code", placeholder="8 characters", max_chars=8).strip().upper()
    if st.button("Connect friend 🤝", type="primary", use_container_width=True):
        ok, msg = add_friend(user_id, code)
        if ok:
            st.success(msg)
            st.session_state.selected_friend = code
            st.rerun()
        else:
            st.error(msg)

if "selected_friend" not in st.session_state:
    st.session_state.selected_friend = None

if friends:
    st.subheader("👭 Friends")
    labels = [f["name"] for f in friends]
    ids = [f["friend_id"] for f in friends]
    current_index = ids.index(st.session_state.selected_friend) if st.session_state.selected_friend in ids else 0
    choice = st.selectbox("Choose a friend", labels, index=current_index, label_visibility="collapsed")
    st.session_state.selected_friend = ids[labels.index(choice)]
else:
    st.info("Add a friend using their 8-character Friend Code to start chatting.")
    st.stop()

selected = next(f for f in friends if f["friend_id"] == st.session_state.selected_friend)
friend_id, friend_name = selected["friend_id"], selected["name"]

st.markdown(f'<div class="card"><h3 style="margin:0">🟢 {html.escape(friend_name)}</h3><div class="small">Real person-to-person conversation • messages sync every 2 seconds</div></div>', unsafe_allow_html=True)

messages = get_messages(user_id, friend_id)
chat_html = '<div class="chatbox">'
if not messages:
    chat_html += '<p style="text-align:center;color:#888;margin-top:35vh">No messages yet. Say hello 👋</p>'
for m in messages:
    mine = m["sender_id"] == user_id
    cls = "me" if mine else "friend"
    who = "You" if mine else friend_name
    try:
        dt = datetime.fromisoformat(str(m["created_at"]).replace("Z", "+00:00"))
        time_text = dt.astimezone().strftime("%d %b, %I:%M %p")
    except Exception:
        time_text = ""
    safe_text = html.escape(str(m["message"])).replace("\n", "<br>")
    chat_html += f'<div class="bubble {cls}"><b>{html.escape(who)}</b><br>{safe_text}<div class="meta">{time_text}</div></div>'
chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

with st.form("send_message", clear_on_submit=True, border=False):
    text = st.text_input("Message", label_visibility="collapsed", placeholder=f"Message {friend_name}…", max_chars=2000)
    send = st.form_submit_button("Send 💕", type="primary", use_container_width=True)
    if send:
        ok, msg = send_message(user_id, friend_id, text)
        if not ok:
            st.error(msg)
        else:
            st.rerun()
