from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Chat


def register_view(request):
    if request.method == 'POST':
        User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password']
        )
        return redirect('login')
    return render(request, 'core/register.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('home')
    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    chats = Chat.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/home.html', {'chats': chats})



@login_required
def new_chat(request):
    if request.method == "POST":
        title = request.POST["title"]
        chat = Chat.objects.create(user=request.user, title=title)
        return redirect('chat_detail', chat.id)

    return render(request, 'core/new_chat.html')







@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    if request.method == "POST":
        chat.delete()
        return redirect('home')

    return render(request, 'core/delete_chat_confirm.html', {
        'chat': chat
    })



@login_required
def rename_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)

    if request.method == "POST":
        chat.title = request.POST["title"]
        chat.save()
        return redirect('chat_detail', chat.id)

    return render(request, 'core/rename_chat.html', {'chat': chat})

import os
import json
import requests

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from PIL import Image
from io import BytesIO

from .models import Chat


import json
import os
from django.conf import settings

CONFIG_PATH = os.path.join(settings.BASE_DIR, "core", "inputs.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

SYSTEM_START = CONFIG["SYSTEM_START"]
USE_CASES = CONFIG["USE_CASES"]



# ===============================
# CLOUDFLARE IMAGE GENERATION
# ===============================
import os
import requests
from PIL import Image
from io import BytesIO
from django.conf import settings

def generate_image_cf(prompt: str, chat_id: int):
    API_TOKEN = settings.CLOUDFLARE_API_TOKEN
    ACCOUNT_ID = settings.CLOUDFLARE_ACCOUNT_ID

    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    # ✅ Prompt Template
    positive_prompt = f"""
{prompt},
ultra detailed, high quality, sharp focus,
cinematic lighting, realistic textures, 8k, masterpiece,
depth of field, professional concept art
""".strip()

    negative_prompt = """
blurry, low quality, low resolution, noisy,
bad anatomy, deformed, extra fingers, extra hands,
watermark, logo, text, signature
""".strip()

    payload = {
        "prompt": positive_prompt,
        "negative_prompt": negative_prompt,
        "steps": 30,
        "guidance": 7.5,
        "width": 1024,
        "height": 1024
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Cloudflare image generation failed: {response.text}")

    folder = os.path.join(settings.MEDIA_ROOT, f"chat_images/chat_{chat_id}")
    os.makedirs(folder, exist_ok=True)

    existing = len([f for f in os.listdir(folder) if f.endswith(".png")])
    filename = f"image_{existing + 1}.png"
    image_path = os.path.join(folder, filename)

    image = Image.open(BytesIO(response.content))
    image.save(image_path)

    return settings.MEDIA_URL + f"chat_images/chat_{chat_id}/{filename}"



# ===============================
# GEMINI TEXT GENERATION
# ===============================
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

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        res = requests.post(
            f"{URL}?key={settings.GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        data = res.json()

        return (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "⚠️ AI could not generate content.")
        )

    except Exception:
        return "⚠️ Server error while generating content."


# ===============================
# CHAT API
# ===============================
@csrf_exempt
@login_required
def chat_api_reply(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    data = json.loads(request.body or "{}")

    user_msg = (data.get("message") or "").strip()
    action = data.get("action")

    # save user message
    if user_msg:
        chat.messages.append({
            "sender": "user",
            "content": user_msg,
            "timestamp": timezone.now().isoformat()
        })

    # get last meta
    last_ai = next((m for m in reversed(chat.messages) if m["sender"] == "ai"), None)
    meta = last_ai.get("meta") if last_ai else {"step": "idle"}

    # default keys
    meta.setdefault("image_pending", False)

    reply, options = "", None

    # ===============================
    # PLUS IMAGE MODE START (does NOT break flow)
    # ===============================
    if action == "plus_image":
        meta["image_pending"] = True
        reply = "🖼️ Enter your image prompt (or type `cancel` to stop):"
        options = None

    # ===============================
    # IMAGE PROMPT HANDLER (side feature)
    # ===============================
    elif meta.get("image_pending") is True:
        if user_msg.lower() == "cancel":
            meta["image_pending"] = False

            # repeat current pending question (if any)
            pending_question_text = ""
            pending_options = None

            if isinstance(meta.get("step"), int) and meta.get("use_case") in USE_CASES:
                uc = USE_CASES[meta["use_case"]]
                if meta["step"] < len(uc["questions"]):
                    q = uc["questions"][meta["step"]]
                    pending_question_text = f"<br><br>➡️ <b>{q['question']}</b>"
                    pending_options = q["options"]

            reply = f"✅ Image generation cancelled.{pending_question_text}"
            options = pending_options

        else:
            try:
                image_url = generate_image_cf(user_msg, chat.id)

                # repeat current pending question (if any)
                pending_question_text = ""
                pending_options = None

                if isinstance(meta.get("step"), int) and meta.get("use_case") in USE_CASES:
                    uc = USE_CASES[meta["use_case"]]
                    if meta["step"] < len(uc["questions"]):
                        q = uc["questions"][meta["step"]]
                        pending_question_text = f"<br><br>➡️ <b>{q['question']}</b>"
                        pending_options = q["options"]

                reply = f"""
                🖼️ <strong>Your image is ready!</strong><br><br>
                <img src="{image_url}" style="max-width:100%;border-radius:12px"/><br><br>
                
                {pending_question_text}
                """

                options = pending_options

            except Exception as e:
                reply = f"⚠️ Image generation failed: {str(e)}"
                options = None

            # IMPORTANT: go back to normal flow
            meta["image_pending"] = False

    # ===============================
    # START
    # ===============================
    elif action == "start":
        meta = {"step": "select", "image_pending": False}
        reply = SYSTEM_START["message"]
        options = SYSTEM_START["options"]

    # ===============================
    # SELECT USE CASE
    # ===============================
    elif meta.get("step") == "select":
        if user_msg not in USE_CASES:
            reply = "❌ Please select an option."
            options = SYSTEM_START["options"]
        else:
            uc = USE_CASES[user_msg]
            meta = {
                "step": 0,
                "use_case": user_msg,
                "answers": {},
                "image_pending": False
            }
            q = uc["questions"][0]
            reply = q["question"]
            options = q["options"]

    # ===============================
    # QUESTION FLOW
    # ===============================
    elif isinstance(meta.get("step"), int):
        uc = USE_CASES[meta["use_case"]]
        q = uc["questions"][meta["step"]]

        meta["answers"][q["key"]] = user_msg
        meta["step"] += 1

        if meta["step"] < len(uc["questions"]):
            nq = uc["questions"][meta["step"]]
            reply = nq["question"]
            options = nq["options"]

        else:
            # final
            if meta["use_case"] == "image":
                prompt = (
                    f"{meta['answers']['prompt']}, "
                    f"{meta['answers']['style']} style, "
                    f"{meta['answers']['theme']} theme"
                )

                try:
                    image_url = generate_image_cf(prompt, chat.id)

                    reply = f"""
                    🖼️ <strong>Your image is ready!</strong><br><br>
                    <img src="{image_url}" style="max-width:100%;border-radius:12px"/><br><br>
                
                    ✅ Done! What would you like to do next?
                    """

                    options = ["Continue", "Start New"]
                    meta["step"] = "done"

                except Exception as e:
                    reply = f"⚠️ Image generation failed: {str(e)}"
                    options = ["Continue", "Start New"]
                    meta["step"] = "done"

            else:
                content = generate_content(uc["role"], meta["answers"])
                reply = f"""{content}<br><br>✅ Done! What would you like to do next?"""
                options = ["Continue", "Start New"]
                meta["step"] = "done"

    # ===============================
    # DONE
    # ===============================
    elif meta.get("step") == "done":
        if user_msg == "Start New":
            chat.messages = []
            meta = {"step": "select", "image_pending": False}
            reply = SYSTEM_START["message"]
            options = SYSTEM_START["options"]

        elif user_msg == "Continue":
            meta = {"step": "select", "image_pending": False}
            reply = SYSTEM_START["message"]
            options = SYSTEM_START["options"]

        else:
            reply = "Please choose an option."
            options = ["Continue", "Start New"]

    else:
        meta = {"step": "select", "image_pending": False}
        reply = SYSTEM_START["message"]
        options = SYSTEM_START["options"]

    # save AI message
    chat.messages.append({
        "sender": "ai",
        "content": reply,
        "timestamp": timezone.now().isoformat(),
        "meta": meta
    })

    chat.save()

    return JsonResponse({
        "reply": reply,
        "options": options,
        "step": meta.get("step")
    })


# ===============================
# CHAT PAGE
# ===============================
@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, user=request.user)
    return render(request, "core/chat.html", {"chat": chat})
