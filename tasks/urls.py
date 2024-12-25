from django.urls import path

from .views import rate_user_task_assign, subtasks_list, swod_analysis, tasks_list

urlpatterns = [
    path("", tasks_list, name="tasks_list"),
    path("swod/", swod_analysis, name="swod_analysis"),
    path("subtasks/<int:task_id>/", subtasks_list, name="subtasks_list"),
    path(
        "rate_user_task_assign/<int:task_id>/<int:staff_id>/",
        rate_user_task_assign,
        name="rate_user_task_assign",
    ),
]
