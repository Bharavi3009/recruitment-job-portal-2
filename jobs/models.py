from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="candidate_profile")
    phone = models.CharField(max_length=15)
    skills = models.TextField(blank=True)
    education = models.TextField(blank=True, help_text="Education, qualification and institution")
    experience = models.TextField(blank=True, help_text="Work experience, internships or projects")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Job(models.Model):
    CATEGORY_CHOICES = [(x,x) for x in ["Software & IT", "Data & Analytics", "Design", "Marketing", "Finance", "Human Resources", "Sales", "Customer Support", "Other"]]
    TYPE_CHOICES = [(x,x) for x in ["Full-time", "Part-time", "Internship", "Contract", "Remote"]]
    EXPERIENCE_CHOICES = [(x,x) for x in ["Fresher", "0-2 years", "2-5 years", "5+ years"]]
    title = models.CharField(max_length=150)
    company = models.CharField(max_length=150)
    location = models.CharField(max_length=100)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="Software & IT")
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="Full-time")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default="Fresher")
    description = models.TextField()
    requirements = models.TextField()
    salary = models.CharField(max_length=100, blank=True)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
    def __str__(self): return f"{self.title} - {self.company}"
    @property
    def is_open(self): return self.is_active and self.deadline >= timezone.localdate()

class Application(models.Model):
    STATUS_CHOICES = [("Applied", "Applied"), ("Shortlisted", "Shortlisted"), ("Interview", "Interview"), ("Rejected", "Rejected")]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    cv = models.FileField(upload_to="cvs/", validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])])
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Applied")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-applied_at"]
        constraints = [models.UniqueConstraint(fields=["job", "candidate"], name="unique_job_candidate")]
    def __str__(self): return f"{self.candidate.username} - {self.job.title}"

class SavedJob(models.Model):
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")
    saved_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-saved_at"]
        constraints = [models.UniqueConstraint(fields=["candidate", "job"], name="unique_saved_job_candidate")]
    def __str__(self): return f"{self.candidate.username} saved {self.job.title}"
