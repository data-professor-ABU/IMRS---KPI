from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import CustomUser
from common.models import BaseModel


class Tasks(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    description = models.TextField(_("Description"))
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")


class SubTasksCategory(BaseModel):
    title = models.CharField(_("Title"), max_length=255)
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = _("Sub Task Category")
        verbose_name_plural = _("Sub Task Categories")


class SubTasks(BaseModel):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, related_name="sub_tasks")
    title = models.CharField(_("Title"), max_length=255)
    category = models.ForeignKey(
        SubTasksCategory,
        on_delete=models.CASCADE,
        related_name="sub_tasks",
        blank=True,
        null=True,
    )
    min_range = models.IntegerField(_("Min Range"))
    max_range = models.IntegerField(_("Max Range"))
    is_active = models.BooleanField(_("Is Active"), default=True)

    def __str__(self):
        return f"{self.task.title} - {self.title}"

    class Meta:
        verbose_name = _("Sub Task")
        verbose_name_plural = _("Sub Tasks")


class TaskAssignee(BaseModel):
    subtask = models.ForeignKey(
        SubTasks, on_delete=models.CASCADE, related_name="task_assignee"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="task_assignee"
    )
    rating = models.IntegerField(_("Rating"), blank=True, null=True)
    comment = models.TextField(_("Comment"), blank=True, null=True)

    @property
    def user_total_rating(self):
        pass

    def __str__(self):
        return f"{self.subtask.title} - {self.user.username}"

    class Meta:
        verbose_name = _("Task Assignee")
        verbose_name_plural = _("Task Assignees")

    # def save(self, *args, **kwargs):
    #     if self.rating:
    #         rating = int(self.rating)
    #         # check if rating is between task min and max range
    #         if rating < self.subtask.min_range or rating > self.subtask.max_range:
    #             raise ValueError("Rating should be between min and max range")
    #     super(TaskAssignee, self).save(*args, **kwargs)
