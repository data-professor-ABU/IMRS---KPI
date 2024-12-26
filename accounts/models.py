# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel

from .manager import CustomUserManager


class Project(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")


class UserRole(models.TextChoices):
    SUPERADMIN = "superadmin", _("SuperAdmin")
    ADMIN = "admin", _("Admin")
    USER = "user", _("User")


class UserStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    FIRED = "fired", _("Fired")
    HOLIDAY = "holiday", _("Holiday")


class UserPosition(models.TextChoices):
    JUNIOR = "junior", _("Junior")
    MIDDLE = "middle", _("Middle")
    SENIOR = "senior", _("Senior")


class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(
        max_length=20, choices=UserRole.choices, default=UserRole.USER
    )
    # projects = models.ManyToManyField(Project, related_name="users", blank=True)
    current_project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, related_name="users", null=True, blank=True
    )
    position = models.CharField(
        max_length=20, choices=UserPosition.choices, default=UserPosition.JUNIOR
    )
    birth_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(
        max_length=20, choices=UserStatus.choices, default=UserStatus.ACTIVE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("CustomUser")
        verbose_name_plural = _("CustomUsers")


class UserAttendance(BaseModel):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="attendances"
    )

    date = models.DateField()
    late_entry_time = models.CharField("Late Entry Time", max_length=255)
    early_exit_time = models.CharField("Early Exit Time", max_length=255)
    penalty = models.PositiveIntegerField(default=0)

    @property
    def total_minutes(self):
        return self.late_entry_time + self.early_exit_time

    def __str__(self):
        return f"{self.user} - {self.date}"

    class Meta:
        verbose_name = _("UserAttendance")
        verbose_name_plural = _("UserAttendances")
        unique_together = ("user", "date")
