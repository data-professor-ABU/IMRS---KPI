from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import CustomUser
from tasks.models import SubTasks, TaskAssignee, Tasks


@login_required
def create_user_task_assign(request, task_id, staff_id):
    try:
        task = Tasks.objects.get(id=task_id)
        staff_user = CustomUser.objects.get(id=staff_id)

        # Prefetch TaskAssignee for the current user
        rated_subtasks = TaskAssignee.objects.filter(user=staff_user)
        subtasks = SubTasks.objects.filter(task=task, is_active=True).prefetch_related(
            Prefetch(
                "task_assignee",
                queryset=rated_subtasks.order_by("-date"),
                to_attr="rated_data",
            )
        )

        if request.method == "POST":
            subtask_id = request.POST.get("subtask_id")
            rate = float(request.POST.get("rate"))
            comment = request.POST.get("comment")
            date = request.POST.get("date")

            subtask = SubTasks.objects.get(id=subtask_id)
            if rate < subtask.min_range or rate > subtask.max_range:
                messages.error(
                    request,
                    f"Rating should be between {subtask.min_range} and {subtask.max_range}",
                )
                return redirect(
                    "rate_user_task_assign", task_id=task_id, staff_id=staff_id
                )

            # Create or update the TaskAssignee instance
            assignee = TaskAssignee.objects.create(
                subtask=subtask,
                user=staff_user,
                rating=rate,
                comment=comment,
                date=date,
            )

            messages.success(request, "Baho mufaqiyatli saqlandi")
            return redirect("rate_user_task_assign", task_id=task_id, staff_id=staff_id)

        context = {
            "task": task,
            "staff_user": staff_user,
            "subtasks": subtasks,
        }
        return render(
            request,
            "tasks/create_user_subtasks_list.html",
            context,
        )
    except Exception as e:
        messages.error(request, f"Error: {e}")
        raise e


@login_required
def user_task_assigments(request, user_id, task_id=None):
    try:
        from_date = request.GET.get("from_date", "")
        to_date = request.GET.get("to_date", "")

        user = get_object_or_404(CustomUser, id=user_id)
        task_assignments = TaskAssignee.objects.filter(user=user).order_by("-date")
        if task_id:
            task = Tasks.objects.get(id=task_id)
            sub_tasks = SubTasks.objects.filter(task=task)
            task_assignments = task_assignments.filter(subtask__in=sub_tasks)

        if from_date != "" and to_date != "":
            task_assignments = task_assignments.filter(date__range=[from_date, to_date])

        context = {
            "user": user,
            "task": task if task_id else None,
            "sub_tasks": sub_tasks if task_id else None,
            "task_assignments": task_assignments,
            "from_date": from_date,
            "to_date": to_date,
        }
        return render(
            request,
            "tasks/user_task_assignments.html",
            context,
        )
    except Exception as e:
        raise e
