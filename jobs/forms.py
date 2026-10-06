from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Application, CandidateProfile, Job

class CandidateRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    skills = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "skills", "password1", "password2")
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists(): raise forms.ValidationError("An account with this email already exists.")
        return email
    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not phone.isdigit() or not 10 <= len(phone) <= 15: raise forms.ValidationError("Phone must contain 10-15 digits.")
        return phone
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name, user.last_name, user.email = self.cleaned_data["first_name"], self.cleaned_data["last_name"], self.cleaned_data["email"]
        if commit:
            user.save()
            CandidateProfile.objects.create(user=user, phone=self.cleaned_data["phone"], skills=self.cleaned_data["skills"])
        return user

class CandidateProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField()
    class Meta:
        model = CandidateProfile
        fields = ["phone", "skills", "education", "experience"]
        widgets = {"skills": forms.Textarea(attrs={"rows": 3}), "education": forms.Textarea(attrs={"rows": 3}), "experience": forms.Textarea(attrs={"rows": 4})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        self.fields["email"].initial = self.instance.user.email
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.user_id).exists(): raise forms.ValidationError("This email is already in use.")
        return email
    def save(self, commit=True):
        profile = super().save(commit=commit)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit: user.save()
        return profile

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "company", "location", "category", "job_type", "experience_level", "description", "requirements", "salary", "deadline", "is_active"]
        widgets = {"deadline": forms.DateInput(attrs={"type": "date"}), "description": forms.Textarea(attrs={"rows": 5}), "requirements": forms.Textarea(attrs={"rows": 5})}
    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        from django.utils import timezone
        if deadline < timezone.localdate(): raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["cv", "cover_letter"]
        widgets = {"cover_letter": forms.Textarea(attrs={"rows": 6, "placeholder": "Tell the recruiter why you are a good fit..."})}
    def clean_cv(self):
        cv = self.cleaned_data["cv"]
        if cv.size > 5 * 1024 * 1024: raise forms.ValidationError("CV must be 5 MB or smaller.")
        return cv

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]
