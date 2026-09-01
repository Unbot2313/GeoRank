from django.conf import settings
from django.db import models


class Competitor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='competitors',
    )
    name = models.CharField(max_length=150, blank=True)
    url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'url')

    def __str__(self):
        return self.name or self.url

    def latest_analysis(self):
        return (
            self.analyses
            .filter(status='completed')
            .select_related('score')
            .order_by('-created_at')
            .first()
        )


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
    competitor = models.ForeignKey(
        Competitor,
        on_delete=models.CASCADE,
        related_name='analyses',
        null=True,
        blank=True,
    )
    url = models.URLField(max_length=500)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    industry_sector = models.CharField(max_length=100, blank=True)
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
