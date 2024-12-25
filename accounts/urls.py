from django.urls import path

from .views import login_form, logout_view, users_attendance

urlpatterns = [
    path("login/", login_form, name="login"),
    path("logout/", logout_view, name="logout"),
    path("attendance/", users_attendance, name="users_attendance"),
]
