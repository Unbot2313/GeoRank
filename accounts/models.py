from django.db import models

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

    class Meta:
        db_table = 'analysis_userprofile'  # tabla física existente, no cambia

    def __str__(self):
        return f"{self.user.username} ({self.plan_type})"

    def analyses_today_count(self):
        today = timezone.localdate()
        return self.user.analyses.filter(
            created_at__date=today,
            status='completed',
            competitor__isnull=True,
        ).count()

    def can_run_analysis(self):
        if self.plan_type == 'pro':
            return True
        return self.analyses_today_count() < self.FREE_DAILY_LIMIT

    def remaining_today(self):
        if self.plan_type == 'pro':
            return None
        return max(0, self.FREE_DAILY_LIMIT - self.analyses_today_count())