import requests, json
from django.conf import settings

#MODEL = "gemini-2.5-flash-lite"
MODEL = "gemma-3-27b-it"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

def generate_content(role, answers):
    prompt = f"""
You are acting as a {role}.

USER INPUT (JSON):
{json.dumps(answers, indent=2)}

RULES:
- Natural human tone
- Platform best practices
- Clean formatting
- No explanations
- Output only final content
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    res = requests.post(
        f"{URL}?key={settings.GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=30
    )

    return res.json()["candidates"][0]["content"]["parts"][0]["text"]

#GEMINI_API_KEYS2 = ["AIzaSyBfmPRw6ezS2ysCXb7dai4wMWJhE-2TNhU","AIzaSyCQ4fUJ2cJJqu_IxfoF4v8mahhAdzUwKcU","AIzaSyBg9whi06tKKR6KOz8zOiGeU7Vvierr-_w","AIzaSyCsMe0bkfYh4ngzWz-VvVZz4nGl0gTvoN0","AIzaSyAGUG5WdUSDQft8lKvGhx-qUrnobUT-vNo","AIzaSyD54U-jTwxNSIlit3Yd33Hu0s0H9PKJuIw"]
