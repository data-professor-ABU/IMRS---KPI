from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Prefetch, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render

from accounts.models import CustomUser, UserRole
from tasks.models import SubTasks, TaskAssignee, Tasks


@login_required
def tasks_list(request):
    tasks = Tasks.objects.filter(is_active=True)
    return render(request, "tasks/tasks_list.html", {"tasks": tasks})


@login_required
def subtasks_list(request, task_id):
    try:
        task = Tasks.objects.get(id=task_id)
        subtasks = SubTasks.objects.filter(task=task, is_active=True)

        # Annotate total ratings for staff_users, ensuring None becomes 0
        staff_users = (
            CustomUser.objects.filter(is_active=True, role=UserRole.USER)
            .prefetch_related(
                Prefetch(
                    "task_assignee",
                    queryset=TaskAssignee.objects.filter(subtask__in=subtasks),
                    to_attr="rated_data",
                )
            )
            .annotate(
                total_rating=Coalesce(
                    Sum(
                        "task_assignee__rating",
                        filter=Q(task_assignee__subtask__in=subtasks),
                    ),
                    Value(0),
                    output_field=models.FloatField(),
                )
            )
        )
        context = {
            "subtasks": subtasks,
            "task": task,
            "staff_users": staff_users,
        }
        return render(request, "tasks/subtasks_list.html", context)
    except Exception as e:
        raise e
