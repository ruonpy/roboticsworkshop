from django.contrib import admin
from django.utils import timezone

from .models import Competition, DesignSubmission


# ============================================================
# DESIGN SUBMISSION INLINE
# ============================================================

class DesignSubmissionInline(admin.TabularInline):
    """
    Allows managing student designs directly
    from the Competition admin page.
    """

    model = DesignSubmission

    extra = 1

    fields = (
        'student',
        'image_url',
    )

    autocomplete_fields = ['student']


# ============================================================
# COMPETITION ADMIN
# ============================================================

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'end_date',
        'is_active',
        'voting_status',
        'total_submissions',
        'created_at',
    )

    list_filter = (
        'is_active',
        'created_at',
        'end_date',
    )

    search_fields = (
        'title',
    )

    ordering = (
        '-created_at',
    )

    inlines = [
        DesignSubmissionInline
    ]

    readonly_fields = (
        'created_at',
    )

    @admin.display(description="Voting Status")
    def voting_status(self, obj):

        if not obj.is_active:
            return "Inactive"

        if timezone.now() >= obj.end_date:
            return "Finished"

        return "Open"

    @admin.display(description="Total Submissions")
    def total_submissions(self, obj):
        return obj.submissions.count()


# ============================================================
# DESIGN SUBMISSION ADMIN
# ============================================================

@admin.register(DesignSubmission)
class DesignSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'competition',
        'display_vote_count',
        'created_at',
    )

    list_filter = (
        'competition',
        'created_at',
    )

    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
        'image_url',
    )

    autocomplete_fields = [
        'student',
    ]

    readonly_fields = (
        'created_at',
        'display_vote_count',
    )

    ordering = (
        '-created_at',
    )

    @admin.display(description="Votes")
    def display_vote_count(self, obj):
        return obj.vote_count