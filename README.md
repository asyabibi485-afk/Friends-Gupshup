# Friend Gup Shup

Simple real friend-to-friend Streamlit chat using Supabase.

## Streamlit Secrets

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_KEY"
```

## Existing Supabase tables

This app matches the user's current schema:
- `users`: `id`, `friend_id`, `name`, `created_at`
- `friendships`: `id`, `user_id`, `friend_id`, `created_at`
- `messages`: `id`, `sender_id`, `receiver_id`, `message`, `created_at`

No extra SQL is required if those tables, policies, and Realtime are already configured.
