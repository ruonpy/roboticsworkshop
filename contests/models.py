from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Competition(models.Model):
    """
    Manages active design voting events, countdown timers, and event status.
    """

    title = models.CharField(
        max_length=200,
        verbose_name="Competition Title"
    )

    end_date = models.DateTimeField(
        verbose_name="Expiration Timestamp (Countdown Target)"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active Event"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Competition Event"
        verbose_name_plural = "Competition Events"
        ordering = ['-created_at']

    @property
    def voting_is_open(self):
        """
        Returns True only if the competition is manually active
        and the deadline has not passed.
        """
        return self.is_active and timezone.now() < self.end_date

    def __str__(self):
        return f"{self.title} - Deadline: {self.end_date.strftime('%d %b %Y')}"


class DesignSubmission(models.Model):
    """
    Stores individual student design assets and peer votes.
    """

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name="Associated Competition"
    )

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="design_submissions",
        verbose_name="Student Creator"
    )

    image_url = models.URLField(
        max_length=1000,
        verbose_name="Design SVG URL"
    )

    voters = models.ManyToManyField(
        User,
        related_name="voted_designs",
        blank=True,
        verbose_name="Registered Voters"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Design Submission"
        verbose_name_plural = "Design Submissions"
        ordering = ['-created_at']

    @property
    def vote_count(self):
        return self.voters.count()

    def __str__(self):
        return f"(@{self.student.username})"