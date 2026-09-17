import os
import random

try:
    from google import genai
except ImportError:
    genai = None


def _fallback_poetry(name, language, mood):
    if language == "Urdu":
        return (
            f"{name} کے نام ایک چھوٹی سی نظم 🌸\n\n"
            "دوستی وہ خوشبو ہے جو فاصلے مٹا دیتی ہے،\n"
            "ایک مسکراہٹ دل کی دنیا سجا دیتی ہے،\n"
            "سچے دوست مل جائیں تو زندگی حسین لگتی ہے،\n"
            "اور ہر گپ شپ ایک خوبصورت یاد بن جاتی ہے۔ 💕"
        )
    if language == "Roman Urdu":
        return (
            f"{name} ke naam 🌸\n\n"
            "Dosti woh khushboo hai jo faaslay mita deti hai,\n"
            "Ek muskurahat dil ki duniya saja deti hai,\n"
            "Sachay dost mil jayein to zindagi haseen lagti hai,\n"
            "Aur har gup shup ek khoobsurat yaad ban jati hai. 💕"
        )
    return (
        f"For {name} 🌸\n\n"
        "A friend is a little light on cloudy days,\n"
        "A smile that stays in countless ways,\n"
        "Through every laugh and every memory,\n"
        "True friendship makes life feel brighter. 💕"
    )


def generate_ai_poetry(name, language, mood):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if genai and api_key:
        try:
            client = genai.Client(api_key=api_key)
            prompt = (
                f"Write a short original {mood.lower()} poem for a friend named {name}. "
                f"Language: {language}. Keep it warm, respectful, and suitable for a "
                "friendship chat app. Do not claim medical or factual benefits. "
                "Use 4-8 short lines and a few tasteful emojis."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if text:
                return text.strip()
        except Exception:
            pass

    return _fallback_poetry(name, language, mood)


def reply_to_message(message):
    msg = message.lower()
    if any(word in msg for word in ["salam", "assalam", "hello", "hi"]):
        return "Wa Alaikum Assalam! 😊 Chalo aaj thori si gup shup aur poetry ho jaye! 🌸"
    if any(word in msg for word in ["sad", "miss", "yaad"]):
        return "Aww 💕 dosti mein yaadein hi to sab se khoobsurat hoti hain. Ek poetry bhi bhejte hain!"
    if any(word in msg for word in ["poetry", "shayari", "poem"]):
        return "Bilkul! ✍️ Poetry Corner kholte hain—dosti ke naam ek khoobsurat sher! 🌷"
    return random.choice([
        "Hahaha 😄 achha! Phir batao, aaj ki sab se interesting baat kya hai?",
        "Nice! 💕 Friends ke saath choti choti baatein bhi special hoti hain.",
        "Bilkul! 😊 Gup shup continue rakho.",
    ])
