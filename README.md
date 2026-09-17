# Friend Gup Shup — Real Friend Chat

A Streamlit friend-to-friend chat app backed by Supabase. No AI replies are used.

## 1. Supabase setup

1. Create a Supabase project.
2. Open **SQL Editor** and run `supabase_schema.sql` completely.
3. Open **Settings → API Keys** and copy the **Project URL** and **Publishable key**. The older `anon` key also works.

## 2. Streamlit Secrets

In Streamlit Cloud: **Manage app → Settings → Secrets**:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_OR_ANON_KEY"
```

Never put a secret/service-role key in GitHub.

## 3. Deploy

Put all files in the repository root and set the Streamlit entrypoint to `app.py`.

## How chat works

Each device gets a UUID stored in its Streamlit session. A user creates a display name and receives an 8-character Friend Code. Adding a friend creates a friendship in both directions. Messages are stored in the shared Supabase `messages` table and the UI polls every 2 seconds.

### Important limitation

This version is a simple prototype. The SQL policies intentionally allow the app's publishable/anon key to read/write these tables so the server-side Streamlit app can work without Supabase Auth. For a public production chat, add Supabase Auth and strict per-user Row Level Security before storing private conversations.
