from django.db import models

class CVDocument(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Structured CV Information
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    education = models.TextField(null=True, blank=True)  # Store as JSON or plain text
    work_experience = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    projects = models.TextField(null=True, blank=True)
    certifications = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.name if self.name else f"CV {self.id}"
