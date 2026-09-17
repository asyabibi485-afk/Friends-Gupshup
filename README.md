# Friend Gup Shup

Real friend-to-friend chat with no AI replies. Streamlit frontend + Supabase database.

## Fix/deploy steps

1. In Supabase SQL Editor, paste the **entire `supabase_schema.sql`** from this ZIP and click **Run**. You should see `Success. No rows returned`.
2. In Streamlit Cloud → Manage app → Settings → Secrets, add:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "YOUR_SUPABASE_PUBLISHABLE_KEY"
```

`SUPABASE_KEY` or `SUPABASE_ANON_KEY` are also accepted.
3. Save/reboot the Streamlit app.
4. Enter your name and press **Create / Continue**.

### Why the old app failed
The previous SQL created the tables and enabled Row Level Security but did not create policies. With a publishable/anon key, Supabase then blocks inserts/selects. This version includes the required prototype policies. It also accepts `SUPABASE_PUBLISHABLE_KEY` in the configuration check.

### Security note
This prototype has no Supabase Auth. The policies are intentionally open so the app works with its generated session UUID. For a real private chat service, add Supabase Auth and user-scoped RLS policies before storing sensitive conversations.
