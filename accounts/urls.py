from django.urls import path

from .views import login_form, logout_view, staff_line_data, staff_list

urlpatterns = [
    path("login/", login_form, name="login"),
    path("logout/", logout_view, name="logout"),
    path("staffs/", staff_list, name="staff_list"),
    path("staff/<int:user_id>/", staff_line_data, name="staff_line_data"),
]
