from django.contrib import admin

from .models import SubTasks, SubTasksCategory, TaskAssignee, Tasks

# admin.site.register(Tasks)
# admin.site.register(SubTasks)
# admin.site.register(TaskAssignee)


class SubTasksInline(admin.TabularInline):
    model = SubTasks
    extra = 1


@admin.register(Tasks)
class TasksAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    search_fields = ("title",)
    list_filter = ("is_active", "created_at", "updated_at")
    date_hierarchy = "created_at"
    inlines = [SubTasksInline]


@admin.register(SubTasks)
class SubTasksAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    search_fields = ("title",)
    list_filter = ("task", "is_active", "created_at", "updated_at")
    date_hierarchy = "created_at"
    autocomplete_fields = ("task", "category")


@admin.register(TaskAssignee)
class TaskAssigneeAdmin(admin.ModelAdmin):
    list_display = ("subtask", "user", "rating", "comment", "created_at", "updated_at")
    search_fields = ("subtask", "user")
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    autocomplete_fields = ("subtask", "user")


@admin.register(SubTasksCategory)
class SubTasksCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    search_fields = ("title",)
    list_filter = ("is_active", "created_at", "updated_at")
    date_hierarchy = "created_at"
