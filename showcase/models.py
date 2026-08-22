from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .utils import check_and_grant_badges, check_teacher_badges

# 🎮 GAMIFICATION & STUDENT PROFILE CONFIGURATION

class StudentProfile(models.Model):
    """
    Stores extended user data for gamification mechanics (EXP, Level, Ranks)
    and administrative personal details.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile', 
        verbose_name="User Account"
    )
    
    teacher_notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Teacher's Internal Notes"
    )
    
    exp = models.IntegerField(
        default=0, 
        verbose_name="Total Experience Points (EXP)"
    )

    def __str__(self):
        return f"Profile - {self.user.get_full_name() or self.user.username}"

    @property
    def current_level(self):
        """Calculates player level dynamically based on every 100 accumulated EXP points."""
        return (self.exp // 100) + 1

    @property
    def progress_percentage(self):
        """Calculates current level progression ratio for the UI progress bar engine."""
        return self.exp % 100

    @property
    def rank_title(self):
        """Returns dynamic roleplay titles calibrated by user's current gamification stage."""
        lvl = self.current_level
        if lvl >= 15:
            return "👑 Kod Krallığının Efsanesi"
        elif lvl >= 10:
            return "🧙 Kod Büyücüsü"
        elif lvl >= 7:
            return "⚔️ Dijital Şövalye"
        elif lvl >= 4:
            return "🗺️ Teknoloji Kaşifi"
        elif lvl >= 2:
            return "🎒 Genç Maceracı"
        else:
            return "🐣 Yeni Kaşif"

    def gain_xp(self, amount):
        """Triggers localized EXP payload injections and commits safely to database."""
        self.exp += amount
        self.save()

# STUDENT PROJECT ARCHIVE CONFIGURATION

class StudentProject(models.Model):
    """
    Manages operational project logs, student tech stack assignments,
    social appreciation counters (Likes), and peer milestone approvals.
    """
    PROJECT_TYPES = [
        ('scratch', 'Scratch Master'),
        ('python', 'Python Coder'),
    ]

    title = models.CharField(
        max_length=200, 
        verbose_name="Project Title"
    )
    
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='projects', 
        verbose_name="Student Author"
    )
    project_type = models.CharField(
        max_length=10, 
        choices=PROJECT_TYPES, 
        default='scratch', 
        verbose_name="Framework / Track Type"
    )
    description = models.TextField(
        verbose_name="Project Narrative & Overview"
    )
    cover_image = models.ImageField(
        upload_to="project_covers/", 
        null=True, 
        blank=True,
        verbose_name="Showcase Thumbnail"
    )
    scratch_embed_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Scratch Sandbox Embed URL"
    )
    python_project_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Python Repository / Source Code Download URL"
    )
    
    # Engagement Tracking Aggregators
    liked_by = models.ManyToManyField(
        User, 
        related_name='liked_projects', 
        blank=True,
        verbose_name="Subscribed Patrons"
    )
    like_count = models.IntegerField(
        default=0,
        verbose_name="Cached Performance Counter"
    )
    
    # Evaluative Milestones (Teacher Endorsements)
    is_original_idea = models.BooleanField(
        default=False, 
        verbose_name="Instructor Verification: Elite Innovation"
    )
    is_creative_design = models.BooleanField(
        default=False, 
        verbose_name="Instructor Verification: Aesthetic Excellence"
    )

    class Meta:
        verbose_name = "Student Project"
        verbose_name_plural = "Student Projects"

    def __str__(self):
        return f"{self.title} (@{self.student.username})"

    def save(self, *args, **kwargs):
        """Interceptors targeting pipeline automation scripts (Auto EXP Allocation & Badge Checking)"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Phase 1: Reward newly established milestones instantly with 50 EXP tokens
        if is_new:
            profile, created = StudentProfile.objects.get_or_create(user=self.student)
            profile.gain_xp(50)
        
        # Phase 2: Fire system diagnostics to verify user qualification for specific badges
        check_and_grant_badges(self.student)
        check_teacher_badges(self)


# ==========================================================================
# 🏅 BADGES & METRIC ACHIEVEMENTS ENGINE
# ==========================================================================

class Badge(models.Model):
    """
    Blueprint table definitions managing gamification system awards, 
    unlocked criteria configurations, and CSS styling guidelines.
    """
    code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Internal Unique Identity Code"
    )
    title = models.CharField(
        max_length=100, 
        verbose_name="Badge Moniker / Public Name"
    )
    description = models.TextField(
        verbose_name="Target Requirement Criteria"
    )
    icon_class = models.CharField(
        max_length=50, 
        default="fa-award", 
        verbose_name="FontAwesome Presentation Tag Style Class"
    )
    badge_color = models.CharField(
        max_length=20, 
        default="#3B82F6", 
        verbose_name="Color Identity (Hexadecimal Representation)"
    )

    def __str__(self):
        return self.title


class StudentBadge(models.Model):
    """
    Relational lookup system tracking validated user prize allocations 
    accompanied by historical timestamps.
    """
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='earned_badges',
        verbose_name="Recipient Student"
    )
    badge = models.ForeignKey(
        Badge, 
        on_delete=models.CASCADE,
        verbose_name="Acquired Award Blueprint"
    )
    earned_at = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Historical Achievement Timestamp"
    )

    class Meta:
        unique_together = ('student', 'badge')

    def __str__(self):
        return f"{self.student.username} earned: {self.badge.title}"