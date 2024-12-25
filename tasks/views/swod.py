from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render

from accounts.models import CustomUser, UserRole
from tasks.models import SubTasks, TaskAssignee, Tasks


@login_required
def swod_analysis(request):
    # Get all the users
    users = CustomUser.objects.filter(is_active=True, role=UserRole.USER)

    # Get all the tasks
    tasks = Tasks.objects.filter(is_active=True)

    # Get all the subtasks
    subtasks = SubTasks.objects.filter(is_active=True)

    # Create a dictionary to store the ratings
    ratings = {}
    user_totals = {}

    # Iterate over all the users
    for user in users:
        # Create a dictionary to store the ratings of the user
        user_ratings = {}

        total_rating = 0  # Initialize total rating

        # Iterate over all the tasks
        for task in tasks:
            # Get all the subtasks of the task
            task_subtasks = subtasks.filter(task=task)

            # Get all the ratings of the user for the subtasks
            user_subtask_ratings = TaskAssignee.objects.filter(
                user=user, subtask__in=task_subtasks
            )

            # Calculate the sum of the ratings
            total_task_rating = user_subtask_ratings.aggregate(
                total_rating=Coalesce(Sum("rating"), Value(0))
            )["total_rating"]

            # Add the task rating to the user ratings
            user_ratings[task.title] = total_task_rating
            total_rating += total_task_rating  # Add task rating to the total

        # Add the user ratings and total rating to the ratings dictionary
        ratings[user.id] = user_ratings  # Store by user ID
        user_totals[user.id] = total_rating  # Store the total rating by user ID

    context = {
        "users": users,
        "tasks": tasks,
        "ratings": ratings,  # Passing ratings dictionary by user ID
        "user_totals": user_totals,  # Passing user totals by user ID
    }

    return render(request, "tasks/swod_analysis.html", context)
