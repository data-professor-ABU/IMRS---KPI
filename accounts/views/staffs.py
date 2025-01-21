from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import make_aware

from tasks.models import TaskAssignee

from ..models import CustomUser, UserRole


@login_required
def staff_line_data(request, user_id):
    # Static months
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    # Get the target user
    user = CustomUser.objects.get(id=user_id)

    # Define year (current year or user-specified year)
    year = timezone.now().year

    # Initialize a list to hold monthly KPIs
    monthly_kpis = []

    # Iterate through each month to calculate KPIs
    for month_idx in range(1, 13):  # Looping through January to December
        start_date = make_aware(datetime(year, month_idx, 1))
        end_date = (
            make_aware(datetime(year, month_idx + 1, 1))
            if month_idx < 12
            else make_aware(datetime(year + 1, 1, 1))
        )

        # Filter TaskAssignee for the user and date range
        user_subtask_ratings = TaskAssignee.objects.filter(
            user=user, date__range=(start_date, end_date)
        )

        # Calculate the sum of ratings for the user in the month
        total_rating = user_subtask_ratings.aggregate(
            total_rating=Coalesce(Sum("rating"), Value(0))
        )["total_rating"]

        # Append the monthly total to the KPI list
        monthly_kpis.append(round(total_rating, 2))

    context = {
        "user": user,
        "months": months,
        "monthly_kpis": monthly_kpis,
    }

    return render(request, "staffs/staff_line_data.html", context)


@login_required
def staff_list(request):
    users = CustomUser.objects.filter(role=UserRole.USER).order_by(
        "first_name", "last_name"
    )

    context = {
        "users": users,
    }
    return render(request, "staffs/staffs.html", context)
