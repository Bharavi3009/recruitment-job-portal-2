from functools import wraps
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import ApplicationForm, CandidateRegistrationForm, CandidateProfileForm, JobForm, StatusUpdateForm
from .models import Application, Job, SavedJob

def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff: return HttpResponseForbidden("Admin access required.")
        return view_func(request, *args, **kwargs)
    return wrapper

def home(request):
    jobs = Job.objects.filter(is_active=True, deadline__gte=timezone.localdate())[:6]
    return render(request, "jobs/home.html", {"jobs": jobs})

def register(request):
    if request.user.is_authenticated: return redirect("home")
    if request.method == "POST":
        form = CandidateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(); login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect("job_list")
    else: form = CandidateRegistrationForm()
    return render(request, "registration/register.html", {"form": form})

def job_list(request):
    query = request.GET.get("q", "").strip(); location = request.GET.get("location", "").strip()
    category = request.GET.get("category", "").strip(); job_type = request.GET.get("job_type", "").strip(); experience = request.GET.get("experience", "").strip()
    jobs = Job.objects.filter(is_active=True, deadline__gte=timezone.localdate())
    if query: jobs = jobs.filter(Q(title__icontains=query) | Q(company__icontains=query) | Q(description__icontains=query) | Q(requirements__icontains=query))
    if location: jobs = jobs.filter(location__icontains=location)
    if category in dict(Job.CATEGORY_CHOICES): jobs = jobs.filter(category=category)
    if job_type in dict(Job.TYPE_CHOICES): jobs = jobs.filter(job_type=job_type)
    if experience in dict(Job.EXPERIENCE_CHOICES): jobs = jobs.filter(experience_level=experience)
    saved_ids = set(SavedJob.objects.filter(candidate=request.user).values_list("job_id", flat=True)) if request.user.is_authenticated and not request.user.is_staff else set()
    context = {"jobs": jobs, "query": query, "location": location, "category": category, "job_type": job_type, "experience": experience, "categories": Job.CATEGORY_CHOICES, "job_types": Job.TYPE_CHOICES, "experience_levels": Job.EXPERIENCE_CHOICES, "saved_ids": saved_ids}
    return render(request, "jobs/job_list.html", context)

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    applied = request.user.is_authenticated and Application.objects.filter(job=job, candidate=request.user).exists()
    saved = request.user.is_authenticated and not request.user.is_staff and SavedJob.objects.filter(job=job, candidate=request.user).exists()
    return render(request, "jobs/job_detail.html", {"job": job, "applied": applied, "saved": saved})

@login_required
def toggle_saved_job(request, job_id):
    if request.user.is_staff:
        messages.error(request, "Admin accounts cannot save candidate jobs."); return redirect("job_detail", pk=job_id)
    job = get_object_or_404(Job, pk=job_id)
    saved, created = SavedJob.objects.get_or_create(candidate=request.user, job=job)
    if not created: saved.delete(); messages.info(request, "Job removed from your saved list.")
    else: messages.success(request, "Job saved for later.")
    return redirect(request.POST.get("next") or "saved_jobs")

@login_required
def saved_jobs(request):
    if request.user.is_staff: return redirect("dashboard")
    jobs = Job.objects.filter(saved_by__candidate=request.user, is_active=True).distinct()
    return render(request, "jobs/saved_jobs.html", {"jobs": jobs})

@login_required
def candidate_profile(request):
    if request.user.is_staff: return redirect("dashboard")
    from .models import CandidateProfile
    profile, _ = CandidateProfile.objects.get_or_create(user=request.user, defaults={"phone": ""})
    if request.method == "POST":
        form = CandidateProfileForm(request.POST, instance=profile)
        if form.is_valid(): form.save(); messages.success(request, "Your profile has been updated."); return redirect("candidate_profile")
    else: form = CandidateProfileForm(instance=profile)
    return render(request, "jobs/profile.html", {"form": form})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if not job.is_open: messages.error(request, "This job is no longer accepting applications."); return redirect("job_detail", pk=job.pk)
    if request.user.is_staff: messages.error(request, "Admin accounts cannot apply for jobs."); return redirect("job_detail", pk=job.pk)
    if Application.objects.filter(job=job, candidate=request.user).exists(): messages.info(request, "You have already applied for this job."); return redirect("my_applications")
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False); application.job = job; application.candidate = request.user; application.save()
            messages.success(request, "Application submitted successfully."); return redirect("my_applications")
    else: form = ApplicationForm()
    return render(request, "jobs/apply.html", {"form": form, "job": job})

@login_required
def my_applications(request):
    applications = Application.objects.filter(candidate=request.user).select_related("job")
    return render(request, "jobs/my_applications.html", {"applications": applications, "statuses": ["Applied", "Shortlisted", "Interview", "Rejected"]})

@admin_required
def dashboard(request):
    job_rows = Job.objects.annotate(application_count=Count("applications"))
    status_counts = [{"label": label, "count": Application.objects.filter(status=label).count()} for label, _ in Application.STATUS_CHOICES]
    max_status = max([x["count"] for x in status_counts] or [0]) or 1
    for row in status_counts: row["width"] = int(row["count"] * 100 / max_status)
    context = {"job_rows": job_rows, "job_count": Job.objects.count(), "active_job_count": Job.objects.filter(is_active=True, deadline__gte=timezone.localdate()).count(), "application_count": Application.objects.count(), "candidate_count": User.objects.filter(is_staff=False).count(), "shortlisted_count": Application.objects.filter(status="Shortlisted").count(), "interview_count": Application.objects.filter(status="Interview").count(), "rejected_count": Application.objects.filter(status="Rejected").count(), "status_counts": status_counts}
    return render(request, "jobs/dashboard.html", context)

@admin_required
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid(): form.save(); messages.success(request, "Job opening created."); return redirect("dashboard")
    else: form = JobForm()
    return render(request, "jobs/job_form.html", {"form": form, "title": "Add Job"})

@admin_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job)
        if form.is_valid(): form.save(); messages.success(request, "Job opening updated."); return redirect("dashboard")
    else: form = JobForm(instance=job)
    return render(request, "jobs/job_form.html", {"form": form, "title": "Edit Job"})

@admin_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST": job.delete(); messages.success(request, "Job opening deleted."); return redirect("dashboard")
    return render(request, "jobs/job_confirm_delete.html", {"job": job})

@admin_required
def application_list(request):
    applications = Application.objects.select_related("job", "candidate").all(); status = request.GET.get("status", "")
    if status in dict(Application.STATUS_CHOICES): applications = applications.filter(status=status)
    return render(request, "jobs/application_list.html", {"applications": applications, "status": status})

@admin_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if request.method == "POST":
        form = StatusUpdateForm(request.POST, instance=application)
        if form.is_valid(): form.save(); messages.success(request, "Application status updated."); return redirect("application_list")
    else: form = StatusUpdateForm(instance=application)
    return render(request, "jobs/status_form.html", {"form": form, "application": application})
