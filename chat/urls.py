from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("chat/user/list/", views.user_list, name="chat_user_list"),
    path("chat/user/<str:username>/", views.chat_view, name="chat_user"),
]
