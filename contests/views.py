from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.views.decorators.http import require_POST

from .models import Competition, DesignSubmission


# ============================================================
# SETTINGS
# ============================================================

MAX_VOTES_PER_COMPETITION = 3


# ============================================================
# SHOWCASE
# ============================================================

@login_required
def contests_showcase(request):
    """
    Displays the active competition showcase.

    During the competition:
    - Designs are shown in random order.
    - Vote counts are hidden.
    - Podium is hidden.

    After the competition:
    - Top 3 designs are displayed on the podium.
    - Vote counts are visible.
    """

    # ---------------------------------------------------------
    # Find active competition
    # ---------------------------------------------------------

    active_competition = (
        Competition.objects
        .filter(is_active=True)
        .first()
    )

    if not active_competition:
        return render(
            request,
            'contests/contests.html',
            {
                'competition': None,
            }
        )

    # ---------------------------------------------------------
    # Competition status
    # ---------------------------------------------------------

    voting_is_open = active_competition.voting_is_open

    # ---------------------------------------------------------
    # User's votes
    # ---------------------------------------------------------

    user_voted_ids = set(
        active_competition.submissions
        .filter(voters=request.user)
        .values_list('id', flat=True)
    )

    user_vote_count = len(user_voted_ids)

    remaining_votes = max(
        MAX_VOTES_PER_COMPETITION - user_vote_count,
        0
    )

    # ---------------------------------------------------------
    # Get submissions
    # ---------------------------------------------------------

    submissions_qs = (
        active_competition.submissions
        .select_related('student')
        .annotate(
            total_votes=Count(
                'voters',
                distinct=True
            )
        )
    )

    # ---------------------------------------------------------
    # DURING COMPETITION
    #
    # Random order prevents first-position advantage.
    # ---------------------------------------------------------

    if voting_is_open:

        submissions = list(
            submissions_qs.order_by('?')
        )

        # No podium during voting.
        podium_designs = []

        other_submissions = submissions

    # ---------------------------------------------------------
    # AFTER COMPETITION
    #
    # Show actual results.
    # ---------------------------------------------------------

    else:

        submissions = list(
            submissions_qs.order_by(
                '-total_votes',
                '-created_at'
            )
        )

        # Top 3 winners
        podium_designs = submissions[:3]

        # Remaining designs
        other_submissions = submissions[3:]

    # ---------------------------------------------------------
    # Context
    # ---------------------------------------------------------

    context = {
        'competition': active_competition,

        # Competition status
        'voting_is_open': voting_is_open,

        # All designs
        'submissions': submissions,

        # Results
        'podium_designs': podium_designs,
        'other_submissions': other_submissions,

        # User voting information
        'user_voted_ids': user_voted_ids,
        'user_vote_count': user_vote_count,
        'remaining_votes': remaining_votes,

        # Voting limit
        'max_votes': MAX_VOTES_PER_COMPETITION,
    }

    return render(
        request,
        'contests/contests.html',
        context
    )


# ============================================================
# VOTE
# ============================================================

@login_required
@require_POST
def vote(request, submission_id):
    """
    Registers one vote for a design.

    Rules:
    - User must be logged in.
    - Competition must still be open.
    - User cannot vote for their own design.
    - User can vote for maximum 3 different designs.
    - A vote cannot be removed.
    """

    # ---------------------------------------------------------
    # Find submission
    # ---------------------------------------------------------

    submission = get_object_or_404(
        DesignSubmission.objects.select_related(
            'competition',
            'student'
        ),
        id=submission_id
    )

    competition = submission.competition

    # ---------------------------------------------------------
    # Competition must be open
    # ---------------------------------------------------------

    if not competition.voting_is_open:

        return JsonResponse(
            {
                'status': 'error',
                'message': 'Bu yarışmanın oylaması sona ermiştir.'
            },
            status=400
        )

    # ---------------------------------------------------------
    # Prevent self-voting
    # ---------------------------------------------------------

    if submission.student == request.user:

        return JsonResponse(
            {
                'status': 'error',
                'message': 'Kendi tasarımınıza oy veremezsiniz.'
            },
            status=400
        )

    # ---------------------------------------------------------
    # Check if already voted
    # ---------------------------------------------------------

    already_voted = submission.voters.filter(
        id=request.user.id
    ).exists()

    if already_voted:

        return JsonResponse(
            {
                'status': 'error',
                'message': 'Bu tasarıma zaten oy verdiniz.'
            },
            status=400
        )

    # ---------------------------------------------------------
    # Count user's existing votes
    # ---------------------------------------------------------

    current_vote_count = (
        competition.submissions
        .filter(
            voters=request.user
        )
        .count()
    )

    # ---------------------------------------------------------
    # Maximum vote limit
    # ---------------------------------------------------------

    if current_vote_count >= MAX_VOTES_PER_COMPETITION:

        return JsonResponse(
            {
                'status': 'error',
                'message': (
                    f'En fazla {MAX_VOTES_PER_COMPETITION} '
                    'tasarıma oy verebilirsiniz.'
                ),
                'vote_limit_reached': True,
                'user_vote_count': current_vote_count,
                'remaining_votes': 0,
                'max_votes': MAX_VOTES_PER_COMPETITION,
            },
            status=400
        )

    # ---------------------------------------------------------
    # Save vote
    # ---------------------------------------------------------

    submission.voters.add(request.user)

    current_vote_count += 1

    remaining_votes = max(
        MAX_VOTES_PER_COMPETITION - current_vote_count,
        0
    )

    # ---------------------------------------------------------
    # Response
    # ---------------------------------------------------------

    return JsonResponse(
        {
            'status': 'success',
            'action': 'added',

            'submission_id': submission.id,
            'total_votes': submission.voters.count(),
            
            'user_vote_count': current_vote_count,
            'remaining_votes': remaining_votes,
            'max_votes': MAX_VOTES_PER_COMPETITION,
        }
    )