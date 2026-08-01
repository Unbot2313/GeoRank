from django.db import models


class Analysis(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
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
