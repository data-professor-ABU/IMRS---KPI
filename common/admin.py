from django.contrib import admin

# import group admin
from django.contrib.auth.admin import GroupAdmin

# unregister GroupAdmin
# admin.site.unregister(GroupAdmin)
admin.site.site_header = "KPI Reporting System"
admin.site.site_title = "KPI Reporting System"
admin.site.index_title = "Welcome to KPI Reporting System"
