from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import StudentProject, StudentProfile

# ==========================================================================
# 🏠 CORE DASHBOARD & PROJECT SHOWCASE VIEWS
# ==========================================================================

def homepage(request):
    """
    Renders the primary student project showcase dashboard.
    Handles server-side filtering, case-insensitive search queries,
    dynamic metrics sorting, and paginated response payloads.
    """
    # Establish base dataset ordered by newest entries first
    project_list = StudentProject.objects.all().order_by('-id')
    
    # 1. Processing Advanced Search Filter (Student Name, Username or Description)
    search_query = request.GET.get('q', '').strip()
    if search_query:
        project_list = project_list.filter(
            Q(student__first_name__icontains=search_query) | 
            Q(student__last_name__icontains=search_query) |
            Q(student__username__icontains=search_query) |
            Q(description__icontains=search_query)
        )
        
    # 2. Processing Track Type Segment Filter (Scratch or Python tracks)
    project_type = request.GET.get('type', '').strip().lower()
    if project_type in ['scratch', 'python']:
        project_list = project_list.filter(project_type=project_type)
        
    # 3. Processing Engagement Sorting Metrics (Newest timeline vs. Popularity metrics)
    sort_by = request.GET.get('sort', 'newest').strip().lower()
    if sort_by == 'popular':
        project_list = project_list.order_by('-like_count', '-id')
    else:
        project_list = project_list.order_by('-id')

    # 4. Server-Side Pagination Gateway: Bound maximum capacity to 9 cards per view instance
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


# ==========================================================================
# ⚡ ENGAGEMENT MECHANICS & EXP GAMIFICATION ENDPOINTS
# ==========================================================================

@login_required
@require_POST
def like_project(request, project_id):
    """
    Handles secure AJAX requests targeting student project validation workflows.
    Ensures absolute data integrity during competitive user interactions and 
    triggers specialized EXP rewards based on roleplay relationships.
    """
    project = get_object_or_404(StudentProject, id=project_id)
    user = request.user

    # Prevent duplicated appreciation logs (No rollback option allowed)
    if user in project.liked_by.all():
        return JsonResponse({
            'status': 'error', 
            'message': 'Zaten beğendiniz.'
        }, status=400)

    # Register user signature and increment cached performance counters safely
    project.liked_by.add(user)
    project.like_count += 1
    project.save()

    # Gamification Algorithm: Initialize or retrieve profiles to dispatch EXP rewards
    project_owner_profile, _ = StudentProfile.objects.get_or_create(user=project.student)
    liker_profile, _ = StudentProfile.objects.get_or_create(user=user)

    # Distribute calibrated EXP weights depending on interaction type
    if project.student == user:
        project_owner_profile.gain_xp(5)
    else:
        liker_profile.gain_xp(2)
        project_owner_profile.gain_xp(10)

    # Dispatches structured operational payloads to the client-side JavaScript engine
    return JsonResponse({
        'status': 'success',
        'like_count': project.like_count
    })


# ==========================================================================
# 📊 STUDENT PROFILE & ACADEMIC PORTAL VIEWS
# ==========================================================================

@login_required
def student_dashboard(request):
    """
    Compiles isolated student profile achievements, earned badges, 
    and customized progression metrics for the logged-in student.
    """
    my_projects = StudentProject.objects.filter(student=request.user).order_by('-id')
    
    context = {
        'projects': my_projects,
        'student': request.user,
    }
    return render(request, 'dashboard.html', context)