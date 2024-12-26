from django.urls import path

from .views import login_form, logout_view, save_analyze_attendance, users_attendance

urlpatterns = [
    path("login/", login_form, name="login"),
    path("logout/", logout_view, name="logout"),
    path("attendance/", users_attendance, name="users_attendance"),
    path("attendance/save/", save_analyze_attendance, name="save_analyze_attendance"),
]
