# 💬 Friend Gup Shup — Real Friend Chat

A simple **real person-to-person** chat app built with Streamlit + Supabase. There are no AI-generated replies.

## Features
- Real messages shared between different phones/browsers
- 8-character Friend Code instead of exposing a long UUID
- Adding a friend creates the connection for both people
- Messages refresh automatically every 2 seconds
- Responsive mobile-friendly interface
- Message escaping and 2,000-character limit
- Supabase database is the shared source of truth

## Deploy on Streamlit Community Cloud

### 1. Create Supabase
Create a Supabase project, open **SQL Editor**, and run `supabase_schema.sql`.

### 2. Add Streamlit Secrets
In your Streamlit app open **Manage app → Settings → Secrets** and add:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_KEY"
```

Do **not** commit the real key to GitHub.

### 3. Deploy
Set the main file to:

```text
app.py
```

The app installs dependencies from `requirements.txt`.

## How two friends chat
1. Person A opens the app and creates a name.
2. The app displays an 8-character Friend Code.
3. Person A sends that code to Person B.
4. Person B creates their own name and enters Person A's code.
5. Both accounts are connected automatically.
6. Either person sends a message; the other browser sees it on the next refresh.

### Important
This is a lightweight prototype without full user authentication. For a public production messenger, add **Supabase Auth, strict Row Level Security, abuse reporting/blocking, rate limiting, message deletion/privacy controls, and server-side authorization**.
