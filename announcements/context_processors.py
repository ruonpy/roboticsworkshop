from .models import Announcement


def active_announcement(request):
    announcement = (
        Announcement.objects
        .filter(
            is_active=True,
            is_popup=True,
        )
        .order_by('-created_at')
        .first()
    )

    if announcement and not announcement.is_visible:
        announcement = None

    return {
        'active_announcement': announcement,
    }