from django.db import models
from django.utils import timezone


class Announcement(models.Model):

    TYPE_CHOICES = [
        ('general', 'General'),
        ('contest', 'Contest'),
        ('homework', 'Homework'),
        ('event', 'Event'),
        ('system', 'System'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Title"
    )

    message = models.TextField(
        verbose_name="Message"
    )

    announcement_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='general',
        verbose_name="Announcement Type"
    )

    redirect_url = models.CharField(
    max_length=500,
    blank=True,
    verbose_name="Redirect URL"
)

    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active"
    )

    is_popup = models.BooleanField(
        default=True,
        verbose_name="Show as Popup"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expiration Date"
    )

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_visible(self):
        if not self.is_active:
            return False

        if self.expires_at and timezone.now() >= self.expires_at:
            return False

        return True