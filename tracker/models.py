from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    FARM_MANAGER = "FARM_MANAGER"
    FIELD_WORKER = "FIELD_WORKER"
    AGRONOMIST = "AGRONOMIST"

    ROLE_CHOICES = [
        (FARM_MANAGER, "Farm Manager"),
        (FIELD_WORKER, "Field Worker"),
        (AGRONOMIST, "Agronomist"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Field(models.Model):
    name = models.CharField(max_length=100)
    crop_type = models.CharField(max_length=100)
    size_acres = models.DecimalField(max_digits=6, decimal_places=2)
    location = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class FarmProject(models.Model):
    STATUS_CHOICES = [
        ("PLANNED", "Planned"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
    ]

    title = models.CharField(max_length=150)
    description = models.TextField()
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLANNED")

    def __str__(self):
        return self.title


class FarmTask(models.Model):
    STATUS_CHOICES = [
        ("TODO", "To Do"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Done"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    project = models.ForeignKey(FarmProject, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to='task_images/', null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="TODO")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="MEDIUM")
    progress_comment = models.TextField(blank=True)

    def __str__(self):
        return self.title


class FarmTaskProgressUpdate(models.Model):
    task = models.ForeignKey(FarmTask, on_delete=models.CASCADE, related_name="progress_updates")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=FarmTask.STATUS_CHOICES)
    comment = models.TextField(blank=True)
    image = models.ImageField(upload_to='task_progress_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task.title} - {self.status} by {self.updated_by.username}"


class FieldRecord(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name="records")
    project = models.ForeignKey(
        FarmProject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="field_records",
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    crop = models.CharField(max_length=100)
    crop_stage = models.CharField(max_length=100)
    advice = models.TextField()
    recorded_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.field.name} - {self.crop} ({self.recorded_on})"
