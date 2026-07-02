from django.utils import timezone

# ==========================================================================
# 🏅 CORE ACHIEVEMENTS & BADGE VERIFICATION ENGINE
# ==========================================================================

def check_and_grant_badges(user):
    """
    Evaluates a student's engagement milestones dynamically.
    Checks published project thresholds and social appreciation milestones
    to allocate specific achievement badges.
    """
    # Lazy import strategy deployed here to bypass critical circular import deadlocks 🌟
    from .models import StudentProject, StudentProfile
    
    profile, _ = StudentProfile.objects.get_or_create(user=user)
    
    # Extract historical tracking metrics for the evaluated student instance
    project_count = StudentProject.objects.filter(student=user).count()
    liked_projects_count = user.liked_projects.count() 
    
    # 1. 🚀 First Step Badge: Awarded upon launching the inaugural deployment
    if project_count >= 1:
        grant_badge(user, 'first_step')

    # 2. 🛠️ Productive Inventor Badge: Awarded upon deploying 3 stable submissions
    if project_count >= 3:
        grant_badge(user, 'productive_inventor')

    # 3. 🏗️ Project Master Badge: Elite milestone for reaching 10 published releases
    if project_count >= 10:
        grant_badge(user, 'project_master')

    # 4. 🤝 Team Player Badge: Earned by backing 5 unique peer applications
    if liked_projects_count >= 5:
        grant_badge(user, 'team_player')

    # 5. 👏 Support Star Badge: Earned by validating 25 unique peer deployments
    if liked_projects_count >= 25:
        grant_badge(user, 'support_star')

    # 6. 🌟 Academy Legend Badge: Divine tier combining extreme metrics (1000+ EXP, 10 Projects, 20 Likes)
    if profile.exp >= 1000 and project_count >= 10 and liked_projects_count >= 20:
        grant_badge(user, 'academy_legend')


# ==========================================================================
# 🎨 INSTRUCTOR EVALUATION & SPECIAL ENDORSEMENTS
# ==========================================================================

def check_teacher_badges(project):
    """
    Triggers automatically when an instructor logs specialized verification 
    payloads or custom milestone approvals inside the Django Administrative suite.
    """
    user = project.student
    
    # 7. 🎨 Idea Hunter Badge: Dispatched via explicit instructor validation for high innovation
    if project.is_original_idea:
        grant_badge(user, 'idea_hunter')
        
    # 8. ✨ Creative Designer Badge: Dispatched via instructor validation for aesthetic excellence
    if project.is_creative_design:
        grant_badge(user, 'creative_designer')


# ==========================================================================
# 💾 DATABASE COMMIT & TRANSACTION GATEWAYS
# ==========================================================================

def grant_badge(user, badge_code):
    """
    Safely commits unique award records into the relational database ledger.
    Leverages atomic validation schemas to avoid duplicated milestone injections.
    """
    from .models import Badge, StudentBadge
    
    try:
        badge = Badge.objects.get(code=badge_code)
        # Deploying get_or_create to insulate database integrity against duplicate rows
        StudentBadge.objects.get_or_create(student=user, badge=badge)
    except Badge.DoesNotExist:
        # Failsafe interceptor preventing system exceptions if a configured token isn't initialized yet
        pass