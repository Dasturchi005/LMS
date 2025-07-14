from django.db import models
from apps.user.models import User
from django.utils import timezone
class Lesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    document = models.FileField(upload_to='docs/', blank=True, null=True)
    assignment = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # 💡 Qadam: vaqtinchalik default bilan qo‘shamiz
    created_at = models.DateTimeField(default=timezone.now)

class HomeworkSubmission(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='homework/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)
    grade = models.IntegerField(null=True, blank=True)