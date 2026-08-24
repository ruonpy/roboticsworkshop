import logging
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from .models import StudentProject

logger = logging.getLogger(__name__)

# HOMEPAGE & PROJECT SHOWCASE

def homepage(request):
    project_list = StudentProject.objects.select_related('student')

    search_query = request.GET.get('q', '').strip()

    if search_query:
        project_list = project_list.filter(
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__username__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    project_type = request.GET.get(
        'type',
        ''
    ).strip().lower()

    if project_type in ['scratch', 'python']:
        project_list = project_list.filter(
            project_type=project_type
        )

    sort_by = request.GET.get(
        'sort',
        'newest'
    ).strip().lower()

    if sort_by == 'popular':
        project_list = project_list.order_by(
            '-like_count',
            '-id'
        )
    else:
        project_list = project_list.order_by('-id')

    paginator = Paginator(
        project_list,
        9
    )

    page_number = request.GET.get(
        'page',
        1
    )

    projects = paginator.get_page(
        page_number
    )

    context = {
        'projects': projects,
        'search_query': search_query,
        'selected_type': project_type,
        'selected_sort': sort_by,
    }

    return render(
        request,
        'index.html',
        context
    )

# LIKE SYSTEM & XP

@login_required
@require_POST
def like_project(request, project_id):
    try:
        with transaction.atomic():
            project = get_object_or_404(
                StudentProject.objects.select_for_update(),
                id=project_id
            )

            user = request.user

            if project.liked_by.filter(
                id=user.id
            ).exists():
                logger.info(
                    "Like rejected: already liked. "
                    "user_id=%s project_id=%s",
                    user.id,
                    project.id
                )

                return JsonResponse(
                    {
                        'status': 'error',
                        'message': 'Zaten beğendiniz.'
                    },
                    status=400
                )

            project.liked_by.add(user)

            project.like_count += 1

            project.save(
                update_fields=['like_count']
            )

            project_owner_profile = project.student.profile

            if project.student == user:
                project_owner_profile.gain_xp(5)

            else:
                liker_profile = user.profile

                liker_profile.gain_xp(2)
                project_owner_profile.gain_xp(10)

        logger.info(
            "Like successful. "
            "user_id=%s project_id=%s project_owner_id=%s",
            user.id,
            project.id,
            project.student.id
        )

        return JsonResponse(
            {
                'status': 'success',
                'like_count': project.like_count
            }
        )

    except Exception:
        logger.exception(
            "Unexpected error while liking project. "
            "user_id=%s project_id=%s",
            request.user.id,
            project_id
        )

        raise

# STUDENT DASHBOARD

@login_required
def student_dashboard(request):
    my_projects = StudentProject.objects.filter(
        student=request.user
    ).order_by('-id')

    context = {
        'projects': my_projects,
        'student': request.user,
    }

    return render(
        request,
        'dashboard.html',
        context
    )