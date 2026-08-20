from django.contrib import admin
from .models import Competition, DesignSubmission


class DesignSubmissionInline(admin.TabularInline):
    """
    Allows adding student design submissions directly within the Competition admin view.
    """
    model = DesignSubmission
    extra = 1
    fields = ('student', 'title', 'image', 'description')
    autocomplete_fields = ['student']


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing voting events and their countdown parameters.
    """
    list_display = ('title', 'end_date', 'is_active', 'total_submissions', 'created_at')
    list_filter = ('is_active', 'created_at', 'end_date')
    search_fields = ('title',)
    inlines = [DesignSubmissionInline]

    @admin.display(description="Total Submissions")
    def total_submissions(self, obj):
        return obj.submissions.count()


@admin.register(DesignSubmission)
class DesignSubmissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for inspecting individual design submissions and voter records.
    """
    list_display = ('student', 'competition', 'display_vote_count', 'created_at')
    list_filter = ('competition', 'created_at')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    filter_horizontal = ('voters',)
    autocomplete_fields = ['student']

    @admin.display(description="Votes")
    def display_vote_count(self, obj):
        return obj.vote_count