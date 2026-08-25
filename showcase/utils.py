import logging

logger = logging.getLogger(__name__)

# CORE ACHIEVEMENTS & BADGE VERIFICATION ENGINE

def check_and_grant_badges(user):
    """
    Checks the student's achievement milestones and grants
    the appropriate badges.
    """
    from .models import StudentProject

    profile = user.profile

    # Student metrics
    project_count = StudentProject.objects.filter(student=user).count()
    liked_projects_count = user.liked_projects.count()

    # 1. First Step
    if project_count >= 1:
        grant_badge(user, 'first_step')

    # 2. Productive Inventor
    if project_count >= 3:
        grant_badge(user, 'productive_inventor')

    # 3. Project Master
    if project_count >= 10:
        grant_badge(user, 'project_master')

    # 4. Team Player
    if liked_projects_count >= 5:
        grant_badge(user, 'team_player')

    # 5. Support Star
    if liked_projects_count >= 25:
        grant_badge(user, 'support_star')

    # 6. Academy Legend
    if (
        profile.exp >= 1000
        and project_count >= 10
        and liked_projects_count >= 20
    ):
        grant_badge(user, 'academy_legend')

# BADGE DATABASE OPERATIONS

def grant_badge(user, badge_code):
    """
    Creates the student's badge record if it does not already exist.
    """
    from .models import Badge, StudentBadge, Notification

    try:
        badge = Badge.objects.get(
            code=badge_code
        )

        student_badge, created = StudentBadge.objects.get_or_create(
            student=user,
            badge=badge
        )

        if created:
            logger.info(
                "Badge awarded. "
                "user_id=%s username=%s badge=%s",
                user.id,
                user.username,
                badge.code
            )

    except Badge.DoesNotExist:
        pass