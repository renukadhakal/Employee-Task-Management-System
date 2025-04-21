from django.shortcuts import render, get_object_or_404
from account.models import User
from django.core.cache import cache
from datetime import datetime, timedelta
from .models import Message
from django.contrib.auth.decorators import login_required


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
