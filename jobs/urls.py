from django.urls import path
from . import views
urlpatterns = [
 path("", views.home, name="home"), path("register/", views.register, name="register"), path("jobs/", views.job_list, name="job_list"), path("jobs/<int:pk>/", views.job_detail, name="job_detail"), path("jobs/<int:job_id>/apply/", views.apply_job, name="apply_job"), path("my-applications/", views.my_applications, name="my_applications"),
 path("saved-jobs/", views.saved_jobs, name="saved_jobs"), path("jobs/<int:job_id>/save/", views.toggle_saved_job, name="toggle_saved_job"), path("profile/", views.candidate_profile, name="candidate_profile"),
 path("dashboard/", views.dashboard, name="dashboard"), path("dashboard/jobs/add/", views.job_create, name="job_create"), path("dashboard/jobs/<int:pk>/edit/", views.job_edit, name="job_edit"), path("dashboard/jobs/<int:pk>/delete/", views.job_delete, name="job_delete"), path("dashboard/applications/", views.application_list, name="application_list"), path("dashboard/applications/<int:pk>/status/", views.update_application_status, name="update_application_status"),
]
