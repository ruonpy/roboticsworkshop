from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q

from .models import StudentProject, StudentProfile


# CORE DASHBOARD & SHOWCASE VIEWS

def homepage(request):
    """
    Renders the primary student project showcase dashboard.
    Handles server-side filtering, case-insensitive search queries,
    dynamic metrics sorting, and paginated response payloads.
    """
    project_list = StudentProject.objects.all().order_by('-id')

    # 1. Processing Search Filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        project_list = project_list.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__username__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 2. Processing Track Type Segment Filter
    project_type = request.GET.get('type', '').strip().lower()
    if project_type in ['scratch', 'python']:
        project_list = project_list.filter(project_type=project_type)

    # 3. Processing Engagement Sorting Metrics
    sort_by = request.GET.get('sort', 'newest').strip().lower()
    if sort_by == 'popular':
        project_list = project_list.order_by('-like_count', '-id')
    else:
        project_list = project_list.order_by('-id')

    # 4. Server-Side Pagination
    paginator = Paginator(project_list, 9)
    page_number = request.GET.get('page', 1)
    projects = paginator.get_page(page_number)

    context = {
        'projects': projects,
        'search_query': search_query,
        'selected_type': project_type,
        'selected_sort': sort_by,
    }

    return render(request, 'index.html', context)


# ENGAGEMENT MECHANICS & EXP GAMIFICATION ENDPOINTS

@login_required
@require_POST
def like_project(request, project_id):
    """
    Handles secure project likes and XP rewards.

    XP rules:
    - Student likes their own project: Project owner -> +5 XP
    - Student likes another student's project: Liker -> +2 XP, Owner -> +10 XP
    """
    with transaction.atomic():
        project = get_object_or_404(
            StudentProject.objects.select_for_update(),
            id=project_id
        )
        user = request.user

        if project.liked_by.filter(id=user.id).exists():
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Zaten beğendiniz.'
                },
                status=400
            )

        # 1. Register Like
        project.liked_by.add(user)
        project.like_count += 1
        project.save(update_fields=['like_count'])

        # 2. Fetch Project Owner Profile
        project_owner_profile, _ = StudentProfile.objects.get_or_create(
            user=project.student
        )

        # 3. Distribute XP
        if project.student == user:
            project_owner_profile.gain_xp(5)
        else:
            liker_profile, _ = StudentProfile.objects.get_or_create(
                user=user
            )
            liker_profile.gain_xp(2)
            project_owner_profile.gain_xp(10)

    # 4. Return Success Response
    return JsonResponse(
        {
            'status': 'success',
            'like_count': project.like_count
        }
    )


# STUDENT PROFILE & DASHBOARD VIEWS

@login_required
def student_dashboard(request):
    """
    Compiles isolated student profile achievements, earned badges,
    and customized progression metrics for the logged-in student.
    """
    my_projects = StudentProject.objects.filter(
        student=request.user
    ).order_by('-id')

    context = {
        'projects': my_projects,
        'student': request.user,
    }

    return render(request, 'dashboard.html', context)