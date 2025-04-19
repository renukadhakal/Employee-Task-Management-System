from django.core.cache import cache
from datetime import datetime


class OnlineNowMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            cache.set(f"online-{request.user.username}", datetime.now(), timeout=60)
        return self.get_response(request)
