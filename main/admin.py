from django.contrib import admin
from .models import CrowdDensity

# Register your models here.
class CrowdDensityAdmin(admin.ModelAdmin):

    fieldsets = [
        ("Title/date", {"fields": ["user_dashboard_title", "user_dashboard_published"]}),
        ("Content", {"fields": [ "user_dashboard_content"]})
    ]

admin.site.register(CrowdDensity, CrowdDensityAdmin)