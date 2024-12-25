from django.urls import path

from .views import (
    create_user_task_assign,
    subtasks_list,
    swod_analysis,
    tasks_list,
    user_task_assigments,
)

urlpatterns = [
    path("", tasks_list, name="tasks_list"),
    path("swod/", swod_analysis, name="swod_analysis"),
    path("subtasks/<int:task_id>/", subtasks_list, name="subtasks_list"),
    # Assigning a task to a user
    path(
        "create/assign/<int:task_id>/<int:staff_id>/",
        create_user_task_assign,
        name="rate_user_task_assign",
    ),
    path(
        "assigments/<int:user_id>/<int:task_id>/",
        user_task_assigments,
        name="user_task_assigments",
    ),
]
