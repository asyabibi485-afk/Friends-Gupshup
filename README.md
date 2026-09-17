# Friend Gup Shup — EASY CHAT

This version removes the visible 8-character Friend Code.

## New flow

1. Create your profile with a username.
2. Tap **Add friend**.
3. Search your friend's username.
4. Tap **Chat**.
5. The app connects and opens the chat automatically.

Example:

`@ali123` → **Add friend** → **Chat**

## Supabase

Run the updated `supabase_schema.sql` once in the Supabase SQL Editor.

If your project already has `users_select`, the migration safely drops and recreates that policy. It also adds a `username` column and a unique username index.

## Streamlit Secrets

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_KEY"
```

You can also use `SUPABASE_PUBLISHABLE_KEY` or `SUPABASE_ANON_KEY`.

## Deploy

Use `app.py` as the Streamlit entry point.
