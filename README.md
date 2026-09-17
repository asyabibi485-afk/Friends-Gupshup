# 💬 Friend Gup Shup — EASY CHAT

This version is intentionally simple.

## How it works

1. Enter your name and username.
2. Tap **Start chatting 💕**.
3. Give your friend your username, for example `@asya123`.
4. Your friend taps **Add friend**.
5. They type `asya123`.
6. They tap **Connect 💕**.
7. The friendship is created for BOTH people automatically.
8. The chat opens immediately.

### There are NO friend requests

No codes, no request/accept screen, and no manual database entries.

## Supabase

Run `supabase_schema.sql` once in the Supabase SQL Editor.

This simple version does not use Supabase Auth. Because of that, the SQL disables RLS on these demo tables so the Streamlit client can work with the publishable/anon key.

For a truly private production chat, add Supabase Auth and user-based RLS later.

## Streamlit Secrets

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_KEY"
```

## Deploy

Use `app.py` as the Streamlit entry point.
