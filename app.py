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
    key = _secret("SUPABASE_KEY") or _secret("SUPABASE_PUBLISHABLE_KEY") or _secret("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


def _require():
    c = _client()
    if c is None:
        if create_client is None:
            raise RuntimeError("Supabase Python package is not installed. Check requirements.txt and redeploy.")
        raise RuntimeError("Supabase is not configured. Add SUPABASE_URL and SUPABASE_KEY in Streamlit Secrets.")
    return c


def normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "").strip())[:40]


def new_friend_code() -> str:
    return secrets.token_hex(4).upper()


def get_profile(friend_code: str):
    try:
        res = _require().table("users").select("id,friend_id,name,created_at").eq("friend_id", friend_code).maybe_single().execute()
        return res.data
    except Exception:
        return None


def create_profile(name: str):
    name = normalize_name(name) or "Friend"
    c = _require()
    for _ in range(5):
        code = new_friend_code()
        try:
            res = c.table("users").insert({"friend_id": code, "name": name}).execute()
            return (res.data or [None])[0]
        except Exception as e:
            if "duplicate" not in str(e).lower() and "unique" not in str(e).lower():
                raise
    raise RuntimeError("Could not create a unique Friend Code. Please try again.")


def update_profile(db_id, name):
    name = normalize_name(name) or "Friend"
    res = _require().table("users").update({"name": name}).eq("id", db_id).execute()
    return (res.data or [None])[0]


def get_user_by_friend_code(friend_code):
    code = (friend_code or "").strip().upper()
    if not code:
        return None
    try:
        return _require().table("users").select("id,friend_id,name").eq("friend_id", code).maybe_single().execute().data
    except Exception:
        return None


def get_friends(user_db_id):
    try:
        res = (
            _require().table("friendships")
            .select("friend_id, created_at")
            .eq("user_id", user_db_id)
            .order("created_at")
            .execute()
        )
        rows = res.data or []
        if not rows:
            return []
        ids = [str(x["friend_id"]) for x in rows]
        users = _require().table("users").select("id,friend_id,name").in_("id", ids).execute().data or []
        by_id = {str(x["id"]): x for x in users}
        return [
            {"db_id": int(x["friend_id"]), "friend_code": by_id.get(str(x["friend_id"]), {}).get("friend_id", ""), "name": by_id.get(str(x["friend_id"]), {}).get("name", "Friend")}
            for x in rows if str(x["friend_id"]) in by_id
        ]
    except Exception as e:
        st.error(f"Could not load friends: {e}")
        return []


def add_friend(user_db_id, friend_code):
    friend = get_user_by_friend_code(friend_code)
    if not friend:
        return False, "No user found with that Friend Code. Ask your friend to share the 8-character code."
    if int(friend["id"]) == int(user_db_id):
        return False, "You cannot add yourself."
    try:
        c = _require()
        # The user's current Supabase schema stores friendship links by numeric users.id.
        c.table("friendships").upsert(
            {"user_id": user_db_id, "friend_id": friend["id"]},
            on_conflict="user_id,friend_id",
        ).execute()
        c.table("friendships").upsert(
            {"user_id": friend["id"], "friend_id": user_db_id},
            on_conflict="user_id,friend_id",
        ).execute()
        return True, f"Connected with {friend['name']}!"
    except Exception as e:
        return False, str(e)


def get_messages(my_code, friend_code):
    try:
        c = _require()
        res = (
            c.table("messages")
            .select("id,sender_id,receiver_id,message,created_at")
            .or_(f"and(sender_id.eq.{my_code},receiver_id.eq.{friend_code}),and(sender_id.eq.{friend_code},receiver_id.eq.{my_code})")
            .order("created_at")
            .execute()
        )
        return res.data or []
    except Exception as e:
        st.error(f"Could not load messages: {e}")
        return []


def send_message(sender_code, receiver_code, message):
    text = (message or "").strip()
    if not text:
        return False, "Message cannot be empty."
    if len(text) > 2000:
        return False, "Message is too long (maximum 2,000 characters)."
    try:
        _require().table("messages").insert({
            "sender_id": sender_code,
            "receiver_id": receiver_code,
            "message": text,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return True, "Sent"
    except Exception as e:
        return False, str(e)


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

if st_autorefresh:
    st_autorefresh(interval=2000, key="chat_refresh")

if create_client is None or not _secret("SUPABASE_URL") or not (_secret("SUPABASE_KEY") or _secret("SUPABASE_PUBLISHABLE_KEY") or _secret("SUPABASE_ANON_KEY")):
    st.error("Supabase is not configured correctly. Check Streamlit Cloud → Manage app → Settings → Secrets.")
    st.code('SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"\nSUPABASE_KEY = "YOUR_PUBLISHABLE_KEY"')
    st.stop()

# Keep the Friend Code in the URL so a refresh does not create a new identity.
query_code = str(st.query_params.get("friend", "")).strip().upper()
if query_code and "friend_code" not in st.session_state:
    profile = get_profile(query_code)
    if profile:
        st.session_state.friend_code = profile["friend_id"]
        st.session_state.user_db_id = profile["id"]
        st.session_state.display_name = profile["name"]
        st.session_state.profile_ready = True

if "profile_ready" not in st.session_state:
    st.session_state.profile_ready = False

if not st.session_state.profile_ready:
    st.markdown('<div class="card"><h3>👋 Create your chat identity</h3><p>Choose a name. We will generate your Friend Code.</p></div>', unsafe_allow_html=True)
    name = st.text_input("Your name", placeholder="e.g. Ali", max_chars=40)
    if st.button("Create / Continue 💕", type="primary", use_container_width=True):
        if not name.strip():
            st.warning("Please enter your name.")
        else:
            try:
                profile = create_profile(name)
                st.session_state.user_db_id = profile["id"]
                st.session_state.friend_code = profile["friend_id"]
                st.session_state.display_name = profile["name"]
                st.session_state.profile_ready = True
                st.query_params["friend"] = profile["friend_id"]
                st.rerun()
            except Exception as e:
                st.error(str(e))
    st.stop()

user_db_id = st.session_state.user_db_id
my_code = st.session_state.friend_code

with st.expander("👤 My profile & Friend Code", expanded=False):
    st.write(f"**{st.session_state.display_name}**")
    st.markdown(f'<div class="codebox">{html.escape(my_code)}</div>', unsafe_allow_html=True)
    st.caption("Share this 8-character Friend Code with your friend.")
    new_name = st.text_input("Change display name", value=st.session_state.display_name, max_chars=40)
    if st.button("Save name", use_container_width=True):
        try:
            profile = update_profile(user_db_id, new_name)
            st.session_state.display_name = profile["name"]
            st.success("Name updated.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

friends = get_friends(user_db_id)

with st.expander("➕ Add a friend", expanded=not friends):
    code = st.text_input("Friend Code", placeholder="8 characters", max_chars=8).strip().upper()
    if st.button("Connect friend 🤝", type="primary", use_container_width=True):
        ok, msg = add_friend(user_db_id, code)
        if ok:
            st.success(msg)
            st.session_state.selected_friend = code
            st.rerun()
        else:
            st.error(msg)

if "selected_friend" not in st.session_state:
    st.session_state.selected_friend = None

if not friends:
    st.info("Add a friend using their 8-character Friend Code to start chatting.")
    st.stop()

friend_codes = [f["friend_code"] for f in friends]
labels = [f["name"] for f in friends]
current_code = st.session_state.selected_friend if st.session_state.selected_friend in friend_codes else friend_codes[0]
choice_index = friend_codes.index(current_code)
choice = st.selectbox("Choose a friend", labels, index=choice_index, label_visibility="collapsed")
st.session_state.selected_friend = friend_codes[labels.index(choice)]
selected = next(f for f in friends if f["friend_code"] == st.session_state.selected_friend)
friend_code = selected["friend_code"]
friend_name = selected["name"]

st.markdown(f'<div class="card"><h3 style="margin:0">🟢 {html.escape(friend_name)}</h3><div class="small">Real person-to-person conversation • refreshes every 2 seconds</div></div>', unsafe_allow_html=True)

messages = get_messages(my_code, friend_code)
chat_html = '<div class="chatbox">'
if not messages:
    chat_html += '<p style="text-align:center;color:#888;margin-top:35vh">No messages yet. Say hello 👋</p>'
for m in messages:
    mine = m["sender_id"] == my_code
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
        ok, msg = send_message(my_code, friend_code, text)
        if not ok:
            st.error(msg)
        else:
            st.rerun()
