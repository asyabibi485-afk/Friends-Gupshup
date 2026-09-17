# Friend Gup Shup — Real Friend Chat

## Streamlit entry point
Use `app.py` as the Main file path. A duplicate `shup/app.py` and `shup/backend.py` are included so the app also works if your Streamlit deployment is still configured with `shup/app.py`.

## Supabase
1. Create a Supabase project.
2. Run `supabase_schema.sql` in SQL Editor.
3. In Streamlit Cloud → Manage app → Settings → Secrets, add:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_KEY = "YOUR_PUBLISHABLE_KEY"
```

4. Reboot the app. Both friends use the same Supabase project.

Do not commit real keys to GitHub.
