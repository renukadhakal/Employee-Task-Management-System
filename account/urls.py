from django.urls import path
from .views import userLogin,index,userLogout 

app_name="account"

urlpatterns = [
    path('', index, name='home'),
    path("login/", userLogin, name="login"),
    path("logout/", userLogout, name="logout"),
   
]