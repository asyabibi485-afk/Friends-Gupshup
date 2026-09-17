# 💬 Friend Gup Shup — Real Chat

This version is a real person-to-person chat portal. It does **not** generate AI replies.

## What changed

- Messages are stored in a shared Supabase database.
- Your friend can send a message from their own browser/device.
- You can answer from your browser/device.
- The chat refreshes automatically every 2 seconds.
- No fake AI messages are inserted.
- Friend IDs allow two users to connect in this simple demo.

## 1. Create Supabase project

Create a free Supabase project and open its SQL Editor.

Paste and run `supabase_schema.sql`.

## 2. Get credentials

In Supabase, copy your project URL and server/API key.

For Streamlit Cloud, put these in App Settings > Secrets:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_SUPABASE_SERVER_KEY"
```

Never commit your real key to GitHub.

## 3. Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 4. Deploy

Push the folder to GitHub and deploy `app.py` with Streamlit Community Cloud.

Add the two Supabase secrets before running the app.

## Important production note

This project is a simple real-chat prototype. It uses a server-side Supabase key and Friend IDs. For a public production messaging service, add Supabase Auth, Row Level Security policies, user profiles, blocking/reporting, message limits, and proper privacy controls.
