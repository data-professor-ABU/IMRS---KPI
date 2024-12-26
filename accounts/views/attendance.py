from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from ..forms import UserAttendanceForm
from ..models import CustomUser, UserAttendance, UserRole
from ..utils import analyze_users_attendance_data


@login_required
def users_attendance(request):
    today = timezone.now()
    form = UserAttendanceForm()
    yesterday = today - timedelta(days=1)
    from_date = request.GET.get("from_date", yesterday)
    to_date = request.GET.get("to_date", today)
    user = request.GET.get("user", None)
    # get users attendances
    users = CustomUser.objects.filter(role=UserRole.USER)
    attendances = UserAttendance.objects.all().order_by("date", "-penalty")
    if from_date and to_date:
        attendances = attendances.filter(date__range=[from_date, to_date])
    if user:
        attendances = attendances.filter(user=user)
    context = {
        "users": users,
        "user_id": user,
        "attendances": attendances,
        "from_date": from_date,
        "to_date": to_date,
        "form": form,
    }
    return render(request, "attendance/attendance.html", context)


@login_required
def save_analyze_attendance(request):
    try:
        with transaction.atomic():
            today = timezone.now()
            if request.method == "POST":
                form = UserAttendanceForm(request.POST, request.FILES)
                if form.is_valid():
                    df = form.save()
                    # save data to db
                    for index, row in df.iterrows():
                        user, _ = CustomUser.objects.get_or_create(
                            email=row["Name"],
                            role=UserRole.USER,
                            defaults={"first_name": row["Name"]},
                        )
                        UserAttendance.objects.create(
                            user=user,
                            date=today,
                            late_entry_time=row["MinutesLate"],
                            early_exit_time=row["MinutesEarlyExit"],
                            penalty=row["Jarima_ball"],
                        )
                    messages.success(request, "Attendance data saved successfully")
                else:
                    messages.error(request, f"Invalid form data: {form.errors}")
            return redirect("users_attendance")
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect("users_attendance")
