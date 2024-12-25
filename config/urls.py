from django.contrib import admin
from django.urls import include, path

from .views import index

urlpatterns = [
    # home
    path("", index, name="index"),
    # admin
    path("admin/panel/", admin.site.urls),
    # accounts
    path("accounts/", include("accounts.urls")),
    # tasks
    path("tasks/", include("tasks.urls")),
]
