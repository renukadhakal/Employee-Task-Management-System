from django.urls import path
from .views import (
    userLogin,
    index,
    userLogout,
    AdminUserCreateView,
    AdminUserListView,
    delete_user_admin,
    AdminUserUpdateView,
    ManagerUserCreateView,
    ManagerUserListView,
    delete_user_manager,
    ManagerUserUpdateView,
    change_password,
    UserUpdateView,
    transfer_employee,
    get_user_profile,
    forget_password_view,
    set_new_password_view,
    verify_otp_view,
)

app_name = "account"

urlpatterns = [
    path("", index, name="home"),
    path("login/", userLogin, name="login"),
    path("logout/", userLogout, name="logout"),
    path("admin-user-list", AdminUserListView.as_view(), name="admin-user-list"),
    path("admin-user-add", AdminUserCreateView.as_view(), name="admin-user-add"),
    path(
        "admin-user-update/<int:pk>/",
        AdminUserUpdateView.as_view(),
        name="admin-user-update",
    ),
    path("profile/update/", UserUpdateView.as_view(), name="profile-update"),
    path("admin-user-delete/<int:id>/", delete_user_admin, name="admin-user-delete"),
    path("manager-user-list", ManagerUserListView.as_view(), name="manager-user-list"),
    path("manager-user-add", ManagerUserCreateView.as_view(), name="manager-user-add"),
    path(
        "manager-user-update/<int:pk>/",
        ManagerUserUpdateView.as_view(),
        name="manager-user-update",
    ),
    path(
        "manager-user-delete/<int:id>/", delete_user_manager, name="manager-user-delete"
    ),
    path("change_password", change_password, name="change_password"),
    path("transfer-employee/", transfer_employee, name="transfer_employee"),
    path("profile/<int:pk>/", get_user_profile, name="user-profile"),
    path("forgot-password/", forget_password_view, name="forgot_password"),
    path("verify-otp/", verify_otp_view, name="verify_otp"),
    path("set-new-password/", set_new_password_view, name="set_new_password"),
]
