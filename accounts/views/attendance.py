from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import CustomUser, UserRole


@login_required
def users_attendance(request):
    staff_users = CustomUser.objects.filter(role=UserRole.USER)
    return render(request, "accounts/attendance.html", {"staff_users": staff_users})
