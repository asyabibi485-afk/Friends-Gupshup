# Friend Gup Shup — Deployment Ready V5

This version has **no backend.py import** and no `backend.configuration_error()` call.

## Streamlit Cloud
- Main file path: `app.py`
- Python: 3.11 recommended
- After replacing the GitHub files, use **Reboot app**.

## Secrets
Use the exact names below:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_KEY"
```

The app also accepts `SUPABASE_PUBLISHABLE_KEY` or `SUPABASE_ANON_KEY` as the key name.

Do not put the real key in GitHub.

## Supabase
Run `supabase_schema.sql` once in the Supabase SQL Editor.
