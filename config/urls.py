from django.contrib import admin
from django.urls import include, path

from .views import dashboard

urlpatterns = [
    # home
    path("", dashboard, name="dashboard"),
    # admin
    path("admin/panel/", admin.site.urls),
    # accounts
    path("accounts/", include("accounts.urls")),
    # tasks
    path("tasks/", include("tasks.urls")),
]
