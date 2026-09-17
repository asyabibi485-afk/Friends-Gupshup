# 💬 Friend Gup Shup

A friendly Streamlit chat portal for friends, poetry and personalized AI poetry.

## Features

- 🏠 Chat-style Gup Shup portal
- 👭 Add and view friends
- ✍️ Urdu, Roman Urdu and English poetry
- 🤖 Gemini-powered personalized poetry
- 💕 Built-in fallback poetry when Gemini is unavailable
- 📱 Responsive Streamlit interface
- 🚀 GitHub + Streamlit Cloud ready

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

For Gemini AI, create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_key_here"
```

The app reads the Streamlit secret and exposes it safely to the backend through the environment.

## Streamlit Cloud

1. Upload this project to a GitHub repository.
2. Open Streamlit Community Cloud.
3. Create a new app and select `app.py`.
4. Add this secret in the app's Secrets section:

```toml
GEMINI_API_KEY = "your_key_here"
```

5. Deploy.

## Important

This is a demo friendship/chat interface. Messages and added friends are stored in the current Streamlit session only; there is no permanent database or real-time multi-user messaging backend.
