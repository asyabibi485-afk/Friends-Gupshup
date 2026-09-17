import streamlit as st
from backend import generate_ai_poetry, reply_to_message
from poetry import POETRY, MOODS, LANGUAGES

st.set_page_config(
    page_title="Friend Gup Shup 💬",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main {background: #fffafc;}
.hero {
    padding: 28px; border-radius: 22px; margin-bottom: 20px;
    background: linear-gradient(135deg,#ffe4ef,#eee5ff);
    text-align:center;
}
.hero h1 {font-size: 42px; margin-bottom: 5px;}
.card {
    padding: 18px; border-radius: 18px; background: white;
    border: 1px solid #f0dce6; margin-bottom: 12px;
}
.chat-left, .chat-right {
    padding: 12px 16px; border-radius: 18px; margin: 8px 0;
    max-width: 82%;
}
.chat-left {background:#f2f2f7; margin-right:auto;}
.chat-right {background:#ffe1ed; margin-left:auto;}
.small {color:#777; font-size:13px;}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"sender": "Sara", "text": "Assalam-o-Alaikum! Aaj ki gup shup kaisi chal rahi hai? 😊"},
        {"sender": "You", "text": "Wa Alaikum Assalam! Sab friends ko poetry bhejni hai. 💕"},
    ]
if "friends" not in st.session_state:
    st.session_state.friends = ["Sara", "Ayesha", "Fizza", "Hina"]

with st.sidebar:
    st.title("💬 Friend Gup Shup")
    page = st.radio(
        "Menu",
        ["🏠 Gup Shup", "👭 Friends", "✍️ Poetry Corner", "🤖 AI Poetry"],
    )
    st.divider()
    st.caption("A friendly space for chats, poetry and memories.")

st.markdown("""
<div class="hero">
<h1>💬 Friend Gup Shup</h1>
<p>Chat • Friendship • Poetry • Memories</p>
</div>
""", unsafe_allow_html=True)

if page == "🏠 Gup Shup":
    st.subheader("🗨️ Friends Chat Portal")
    friend = st.selectbox("Chat with", st.session_state.friends)

    for msg in st.session_state.messages:
        cls = "chat-right" if msg["sender"] == "You" else "chat-left"
        st.markdown(
            f'<div class="{cls}"><b>{msg["sender"]}</b><br>{msg["text"]}</div>',
            unsafe_allow_html=True,
        )

    with st.form("chat_form", clear_on_submit=True):
        text = st.text_input("Write your message…")
        send = st.form_submit_button("Send 💕")
        if send and text.strip():
            st.session_state.messages.append({"sender": "You", "text": text.strip()})
            st.session_state.messages.append(
                {"sender": friend, "text": reply_to_message(text.strip())}
            )
            st.rerun()

elif page == "👭 Friends":
    st.subheader("👭 My Friends")
    cols = st.columns(2)
    for i, friend in enumerate(st.session_state.friends):
        with cols[i % 2]:
            st.markdown(
                f'<div class="card"><h3>🌸 {friend}</h3>'
                f'<p class="small">Friend • Gup Shup Partner</p></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("➕ Add a Friend")
    with st.form("friend_form", clear_on_submit=True):
        name = st.text_input("Friend name")
        add = st.form_submit_button("Add Friend")
        if add and name.strip():
            clean = name.strip()
            if clean not in st.session_state.friends:
                st.session_state.friends.append(clean)
                st.success(f"{clean} added!")
                st.rerun()

elif page == "✍️ Poetry Corner":
    st.subheader("✍️ Poetry Corner")
    language = st.selectbox("Language", list(LANGUAGES.keys()))
    mood = st.selectbox("Mood", list(MOODS.keys()))

    items = POETRY.get(language, {}).get(mood, [])
    if items:
        for item in items:
            st.markdown(f'<div class="card">🌷<br><br>{item}</div>', unsafe_allow_html=True)
    else:
        st.info("Choose another mood to see poetry.")

elif page == "🤖 AI Poetry":
    st.subheader("🤖 AI Friendship Poetry Generator")
    st.write("Generate a short personalized poem for a friend.")

    name = st.text_input("Friend's name", placeholder="e.g. Ayesha")
    language = st.selectbox("Poetry language", ["Urdu", "English", "Roman Urdu"])
    mood = st.selectbox("Poetry mood", ["Friendship", "Funny", "Emotional", "Missing Friend", "Happy"])

    if st.button("✨ Generate Poetry", use_container_width=True):
        if not name.strip():
            st.warning("Please enter your friend's name.")
        else:
            with st.spinner("Writing poetry…"):
                result = generate_ai_poetry(name.strip(), language, mood)
            st.markdown(f'<div class="card">🌸<br>{result}</div>', unsafe_allow_html=True)

st.divider()
st.caption("Friend Gup Shup • Built with Streamlit • For friendly conversations and creative poetry")
