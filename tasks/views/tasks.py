from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
        messages.error(request, f"Xato: {e}")
        return redirect("tasks_list")


@login_required
def rate_user_task_assign(request, task_id, staff_id):
    try:
        task = Tasks.objects.get(id=task_id)
        staff_user = CustomUser.objects.get(id=staff_id)

        # Prefetch TaskAssignee for the current user
        rated_subtasks = TaskAssignee.objects.filter(user=staff_user)
        subtasks = SubTasks.objects.filter(task=task, is_active=True).prefetch_related(
            Prefetch("task_assignee", queryset=rated_subtasks, to_attr="rated_data")
        )

        if request.method == "POST":
            subtask_id = request.POST.get("subtask_id")
            rate = request.POST.get("rate")
            comment = request.POST.get("comment")
            subtask = SubTasks.objects.get(id=subtask_id)

            # Ensure rating falls in the valid range
            if rate:
                rate = int(rate)
                if rate < subtask.min_range or rate > subtask.max_range:
                    messages.error(
                        request,
                        f"Rating should be within the allowed range. ({subtask.min_range} - {subtask.max_range})",
                    )
                    return redirect(request.path_info)

            # Create or update the TaskAssignee instance
            assignee, _ = TaskAssignee.objects.get_or_create(
                subtask=subtask,
                user=staff_user,
            )
            assignee.rating = rate
            assignee.comment = comment
            assignee.save()
            messages.success(request, "Successfully saved.")

        context = {
            "task": task,
            "staff_user": staff_user,
            "subtasks": subtasks,
        }
        return render(
            request,
            "tasks/rate_user_subtasks_list.html",
            context,
        )
    except Exception as e:
        messages.error(request, f"Error: {e}")
        raise e
