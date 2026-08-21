from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q

from .models import StudentProject, StudentProfile


# ============================================================
# HOMEPAGE & PROJECT SHOWCASE
# ============================================================

def homepage(request):
    project_list = StudentProject.objects.all().order_by('-id')

    # Search
    search_query = request.GET.get('q', '').strip()

    if search_query:
        project_list = project_list.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__username__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Project type filter
    project_type = request.GET.get('type', '').strip().lower()

    if project_type in ['scratch', 'python']:
        project_list = project_list.filter(
            project_type=project_type
        )

    # Sorting
    sort_by = request.GET.get('sort', 'newest').strip().lower()

    if sort_by == 'popular':
        project_list = project_list.order_by(
            '-like_count',
            '-id'
        )
    else:
        project_list = project_list.order_by('-id')

    # Pagination
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


# ============================================================
# LIKE SYSTEM & XP
# ============================================================

@login_required
@require_POST
def like_project(request, project_id):

    with transaction.atomic():

        project = get_object_or_404(
            StudentProject.objects.select_for_update(),
            id=project_id
        )

        user = request.user

        # Prevent duplicate likes
        if project.liked_by.filter(id=user.id).exists():
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Zaten beğendiniz.'
                },
                status=400
            )

        # Add like
        project.liked_by.add(user)

        # Update cached like counter
        project.like_count += 1
        project.save(update_fields=['like_count'])

        # Get or create project owner's profile
        project_owner_profile, _ = StudentProfile.objects.get_or_create(
            user=project.student
        )

        # XP distribution
        if project.student == user:

            # Student likes their own project
            project_owner_profile.gain_xp(5)

        else:

            # Student likes another student's project
            liker_profile, _ = StudentProfile.objects.get_or_create(
                user=user
            )

            liker_profile.gain_xp(2)
            project_owner_profile.gain_xp(10)

    return JsonResponse(
        {
            'status': 'success',
            'like_count': project.like_count
        }
    )


# ============================================================
# STUDENT DASHBOARD
# ============================================================

@login_required
def student_dashboard(request):

    my_projects = StudentProject.objects.filter(
        student=request.user
    ).order_by('-id')

    context = {
        'projects': my_projects,
        'student': request.user,
    }

    return render(request, 'dashboard.html', context)