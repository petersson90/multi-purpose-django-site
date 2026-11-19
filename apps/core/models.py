from django.db import models

# Create your models here.
class TimeStampedModel(models.Model):
    """Abstract base adding created/updated timestamps. Reuse it in any app."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
