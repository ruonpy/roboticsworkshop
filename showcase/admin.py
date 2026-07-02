# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile, StudentProject, StudentBadge, Badge

# ==========================================================================
# 🏅 GAMIFICATION BADGES REGISTRATION
# ==========================================================================

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Configuration interface for managing dynamic gamification rewards."""
    list_display = ('title', 'code', 'badge_color')


# ==========================================================================
# 👥 ADVANCED USER & STUDENT PROFILE INTEGRATION (INLINE)
# ==========================================================================

class StudentProfileInline(admin.StackedInline):
    """Inlines student gamification metrics directly into the core User entity view."""
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Workshop Profile Details'


class UserAdmin(BaseUserAdmin):
    """Extends standard authentication dashboard with embedded student parameters."""
    inlines = (StudentProfileInline,)
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name')


# Re-register core User model to implement modified admin layout bindings
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ==========================================================================
# 🚀 STUDENT PROJECT METRICS & EVALUATION SUITE
# ==========================================================================

@admin.register(StudentProject)
class ProjectAdmin(admin.ModelAdmin):
    """
    Manages student project portfolios, features visual data sorting,
    and deploys real-time social metric recalculation listeners.
    """
    list_display = ('get_student_name', 'project_type', 'like_count')
    list_filter = ('project_type',)
    search_fields = ('student__first_name', 'student__last_name', 'student__username')
    filter_horizontal = ('liked_by',)
    
    def get_student_name(self, obj):
        """Resolves structural author metadata cleanly for display columns."""
        return obj.student.get_full_name() or obj.student.username
    get_student_name.short_description = 'Author Name / Moniker'

    def save_related(self, request, form, formsets, change):
        """
        Data Integrity Interceptor: Automatically recalibrates and caches 
        accurate total like counters whenever relation models get modified.
        """
        super().save_related(request, form, formsets, change)
        project = form.instance
        project.like_count = project.liked_by.count()
        project.save()


# ==========================================================================
# 🎖️ HISTORICAL EARNED BADGES TRANSACTIONS
# ==========================================================================

@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    """Logs and monitors certified student achievement prize acquisitions."""
    list_display = ('get_student_name', 'get_badge_title', 'earned_at')
    list_filter = ('badge', 'earned_at')
    search_fields = ('student__first_name', 'student__last_name', 'student__username')

    def get_student_name(self, obj):
        """Resolves recipient credentials safely for lookup views."""
        return obj.student.get_full_name() or obj.student.username
    get_student_name.short_description = 'Recipient Student'

    def get_badge_title(self, obj):
        """Resolves target moniker references from bound entity definitions."""
        return obj.badge.title
    get_badge_title.short_description = 'Acquired Badge'