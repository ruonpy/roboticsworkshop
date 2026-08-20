from django.contrib import admin
from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'announcement_type',
        'is_active',
        'created_at',
    )

    list_filter = (
        'announcement_type',
        'is_active',
        'created_at',
    )

    search_fields = (
        'title',
        'message',
    )

    ordering = (
        '-created_at',
    )