import uuid

from django.db import models


class BaseModel(models.Model):
    key = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["key"]),
        ]

    def __str__(self) -> str:
        return str(self.key)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
