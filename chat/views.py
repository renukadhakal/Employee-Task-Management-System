from django.shortcuts import render, get_object_or_404
from account.models import User
from django.core.cache import cache
from datetime import datetime, timedelta
from .models import Message
from django.contrib.auth.decorators import login_required
import json, requests
import os

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:1b"


@login_required
def user_list(request):
    users = User.objects.exclude(username=request.user.username)
    user_status = []

    for user in users:
        last_seen = cache.get(f"online-{user.username}")
        is_online = last_seen and datetime.now() - last_seen < timedelta(seconds=60)
        user_status.append((user, is_online))

    return render(request, "chat/user_list.html", {"users": user_status})


@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user], receiver__in=[request.user, other_user]
    )
    last_seen = cache.get(f"online-{other_user.username}")
    is_online = last_seen and datetime.now() - last_seen < timedelta(seconds=60)
    return render(
        request,
        "chat/chat.html",
        {"other_user": other_user, "messages": messages, "is_online": is_online},
    )


def format_faq_for_context():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    faq_path = os.path.join(base_dir, "faq.json")
    with open(faq_path, "r", encoding="utf-8") as f:
        faq_data = json.load(f)
    return "\n".join(
        [f"Q: {item['question']}\nA: {item['answer']}" for item in faq_data]
    )


def build_prompt(user_question):
    context = format_faq_for_context()
    return f"""You are a helpful assistant for a task management system.
Use the following FAQ to answer user questions accurately.

{context}

Now, answer this question:
{user_question}
"""


def ask_bot(user_input):
    prompt = build_prompt(user_input)
    response = requests.post(
        OLLAMA_API_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False}
    )
    return response.json()["response"]


@login_required
def chatbot_view(request):
    bot_user, _ = User.objects.get_or_create(
        username="TaskBot", defaults={"email": "bot@example.com", "is_active": False}
    )
    messages = Message.objects.filter(
        sender__in=[request.user, bot_user], receiver__in=[request.user, bot_user]
    )
    return render(
        request,
        "chat/chatbot.html",
        {"other_user": bot_user, "messages": messages, "is_online": True},
    )
