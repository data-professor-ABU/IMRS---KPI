import json
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render

from accounts.models import CustomUser, Project, UserPosition, UserRole
from tasks.models import SubTasks, TaskAssignee, Tasks


@login_required
def dashboard(request):
    today = datetime.now().strftime("%Y-%m-%d")
    a_month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    from_date = request.GET.get("from_date", a_month_ago)
    to_date = request.GET.get("to_date", today)
    # check from_date and to_date if none set default value (a month ago and today)
    position = request.GET.get("position", "")

    # filter users by position
    users = CustomUser.objects.filter(is_active=True, role=UserRole.USER).order_by(
        "first_name", "last_name"
    )
    if position in [UserPosition.JUNIOR, UserPosition.MIDDLE, UserPosition.SENIOR]:
        users = users.filter(position=position)

    # Get all the tasks
    tasks = Tasks.objects.filter(is_active=True)

    # Get all the subtasks
    subtasks = SubTasks.objects.filter(is_active=True)

    # Get all the projects
    projects = Project.objects.filter(is_active=True)

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
            if from_date and to_date:
                user_subtask_ratings = user_subtask_ratings.filter(
                    date__range=[from_date, to_date]
                )
            # Calculate the sum of the ratings
            total_task_rating = user_subtask_ratings.aggregate(
                total_rating=Coalesce(
                    Sum("rating"), Value(0), output_field=models.FloatField()
                )
            )["total_rating"]

            # Add the task rating to the user ratings
            user_ratings[task.title] = total_task_rating
            total_rating += total_task_rating  # Add task rating to the total

        # Add the user ratings and total rating to the ratings dictionary
        ratings[user.full_name] = user_ratings  # Store by user ID
        user_totals[user.full_name] = round(total_rating, 2)

    # calculate the average of company
    user_totals_len = len(user_totals) if len(user_totals) > 0 else 1
    company_total_avg = sum(user_totals.values()) / user_totals_len

    # group user by current_project and calculate the average of each project by user user_totals
    project_avg = {}

    for project in projects:
        project_users = CustomUser.objects.filter(
            role=UserRole.USER, current_project=project, is_active=True
        )
        project_total = sum(
            user_totals[user.full_name]
            for user in project_users
            if user_totals.get(user.full_name) is not None
        )
        project_avg[project.id] = (
            project_total / len(project_users) if len(project_users) > 0 else 1
        )
    # get which project value is greater than company average
    project_above_avg = {}
    for key, value in project_avg.items():
        if value > company_total_avg:
            project_above_avg[key] = value
    # add how much above average to each user total
    users_bonus = {}
    for user in users:
        if user.current_project:
            pr_avr = project_above_avg.get(user.current_project.id)
            if pr_avr and user_totals[user.full_name] > pr_avr:
                bonus = pr_avr * 0.1
                users_bonus[user.full_name] = bonus
                user_totals[user.full_name] += bonus

            elif pr_avr:
                bonus = pr_avr * 0.05
                users_bonus[user.full_name] = bonus
                user_totals[user.full_name] += bonus

    # By user level find max user_totals and set it 100% then calculate other same level users percentage
    j_user = UserPosition.JUNIOR
    m_user = UserPosition.MIDDLE
    s_user = UserPosition.SENIOR
    j_user_totals = {}
    m_user_totals = {}
    s_user_totals = {}
    for user in users:
        if user.position == j_user:
            j_user_totals[user.full_name] = user_totals[user.full_name]
        if user.position == m_user:
            m_user_totals[user.full_name] = user_totals[user.full_name]
        if user.position == s_user:
            s_user_totals[user.full_name] = user_totals[user.full_name]

    j_max = max(j_user_totals.values()) if j_user_totals else None
    m_max = max(m_user_totals.values()) if m_user_totals else None
    s_max = max(s_user_totals.values()) if s_user_totals else None

    users_kpi = {}

    for user in users:
        if user.position == j_user:
            # formula: (user_total / max_total) * 100
            users_kpi[user.full_name] = (
                round((user_totals[user.full_name] / j_max) * 100, 2) if j_max else 0
            )
        if user.position == m_user:
            users_kpi[user.full_name] = (
                round((user_totals[user.full_name] / m_max) * 100, 2) if m_max else 0
            )
        if user.position == s_user:
            users_kpi[user.full_name] = (
                round((user_totals[user.full_name] / s_max) * 100, 2) if s_max else 0
            )

    # convert to_date and from_date to datetime
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")

    context = {
        "users": users,
        "tasks": tasks,
        "ratings": json.dumps(ratings),  # Passing ratings dictionary by user ID
        "user_totals": user_totals,  # Passing user totals by user ID
        "users_bonus": users_bonus,  # Passing user bonus by user ID
        "users_kpi": users_kpi,
        "company_total_avg": round(company_total_avg, 2),
        "users_total": sum(user_totals.values()),
        "total_users_bonus": sum(users_bonus.values()),
        "project_avg": project_avg,
        "project_above_avg": project_above_avg,
        "from_date": from_date,
        "to_date": to_date,
        "position": position,
    }

    return render(request, "dashboard.html", context)
