import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free'),
        ('pro', 'Pro'),
    ]
    FREE_DAILY_LIMIT = 3

    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    plan_type = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')
    company_name = models.CharField(max_length=150, blank=True)
    industry_sector = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.plan_type})"

    def analyses_today_count(self):
       today = timezone.localdate()

       return self.user.analyses.filter(
         created_at__date=today,
         status='completed',
       ).count()

    def can_run_analysis(self):
        if self.plan_type == 'pro':
            return True
        return self.analyses_today_count() < self.FREE_DAILY_LIMIT

    def remaining_today(self):
        if self.plan_type == 'pro':
            return None  # unlimited
        return max(0, self.FREE_DAILY_LIMIT - self.analyses_today_count())


class Analysis(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analyses',
        null=True,
        blank=True,
    )
    url = models.URLField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    raw_content = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.url} - {self.status}"


class Score(models.Model):
    analysis = models.OneToOneField(Analysis, on_delete=models.CASCADE, related_name='score')
    visibility_score = models.IntegerField(default=0)
    readability_score = models.IntegerField(default=0)
    citability_score = models.IntegerField(default=0)

    def __str__(self):
        return f"Scores for {self.analysis.url}"


class Recommendation(models.Model):
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE, related_name='recommendations')
    priority = models.IntegerField(choices=PRIORITY_CHOICES)
    category = models.CharField(max_length=50)
    description = models.TextField()

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.category} - {self.description[:50]}"