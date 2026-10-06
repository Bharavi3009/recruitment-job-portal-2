from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from jobs.models import CandidateProfile, Job


class Command(BaseCommand):
    help = "Create sample admin, candidate and job records."

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(username="admin", defaults={
            "email": "admin@example.com",
            "first_name": "Portal",
            "last_name": "Admin",
            "is_staff": True,
            "is_superuser": True,
        })
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("Admin@12345")
        admin.save()

        candidate, _ = User.objects.get_or_create(username="candidate", defaults={
            "email": "candidate@example.com",
            "first_name": "Demo",
            "last_name": "Candidate",
        })
        candidate.set_password("Candidate@12345")
        candidate.is_staff = False
        candidate.save()
        CandidateProfile.objects.get_or_create(user=candidate, defaults={
            "phone": "9876543210",
            "skills": "Python, Django, SQL, HTML, CSS",
        })

        deadline = timezone.localdate() + timedelta(days=30)
        jobs = [
            {
                "title": "Python Django Developer",
                "company": "TechNova Solutions",
                "location": "Mumbai",
                "description": "Build and maintain web applications using Python and Django.",
                "requirements": "Python, Django, SQL, Git and basic frontend skills.",
                "salary": "₹4 - ₹7 LPA",
            },
            {
                "title": "Junior Web Developer",
                "company": "BrightWeb Labs",
                "location": "Pune",
                "description": "Work with the development team to create responsive web experiences.",
                "requirements": "HTML, CSS, JavaScript and basic Python knowledge.",
                "salary": "₹3 - ₹5 LPA",
            },
            {
                "title": "Software Intern",
                "company": "InnovateHub",
                "location": "Remote",
                "description": "Learn software development while contributing to real projects.",
                "requirements": "Programming fundamentals, problem solving and willingness to learn.",
                "salary": "₹15,000/month",
            },
        ]
        for data in jobs:
            Job.objects.get_or_create(
                title=data["title"],
                company=data["company"],
                defaults={**data, "deadline": deadline, "is_active": True},
            )

        self.stdout.write(self.style.SUCCESS("Sample data created successfully."))
