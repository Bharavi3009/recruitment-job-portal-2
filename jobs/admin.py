from django.contrib import admin
from .models import Application, CandidateProfile, Job, SavedJob


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "saved_at")
    search_fields = ("candidate__username", "job__title")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "category", "job_type", "location", "deadline", "is_active", "created_at")
    list_filter = ("is_active", "deadline", "category", "job_type", "experience_level")
    search_fields = ("title", "company", "location")


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at")
    search_fields = ("user__username", "user__email")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "applied_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("candidate__username", "job__title", "job__company")
