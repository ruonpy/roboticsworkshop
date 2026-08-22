import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Competition, DesignSubmission


logger = logging.getLogger(__name__)


# SETTINGS

MAX_VOTES_PER_COMPETITION = 3


# SHOWCASE

@login_required
def contests_showcase(request):
    """
    Displays the active competition showcase.
    """
    active_competition = (
        Competition.objects
        .filter(is_active=True)
        .first()
    )

    if not active_competition:
        logger.info(
            "Showcase visited but no active competition exists. user_id=%s",
            request.user.id
        )

        return render(
            request,
            'contests/contests.html',
            {
                'competition': None,
            }
        )

    voting_is_open = active_competition.voting_is_open

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

    if voting_is_open:
        submissions = list(
            submissions_qs.order_by('?')
        )

        podium_designs = []
        other_submissions = submissions

    else:
        submissions = list(
            submissions_qs.order_by(
                '-total_votes',
                '-created_at'
            )
        )

        podium_designs = submissions[:3]
        other_submissions = submissions[3:]

    context = {
        'competition': active_competition,
        'voting_is_open': voting_is_open,
        'submissions': submissions,
        'podium_designs': podium_designs,
        'other_submissions': other_submissions,
        'user_voted_ids': user_voted_ids,
        'user_vote_count': user_vote_count,
        'remaining_votes': remaining_votes,
        'max_votes': MAX_VOTES_PER_COMPETITION,
    }

    return render(
        request,
        'contests/contests.html',
        context
    )


# VOTE

@login_required
@require_POST
def vote(request, submission_id):
    """
    Registers one vote for a design.
    """
    try:
        submission = get_object_or_404(
            DesignSubmission.objects.select_related(
                'competition',
                'student'
            ),
            id=submission_id
        )

        competition = submission.competition

        if not competition.voting_is_open:
            logger.warning(
                "Vote rejected: competition closed. "
                "user_id=%s submission_id=%s competition_id=%s",
                request.user.id,
                submission.id,
                competition.id
            )

            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Bu yarışmanın oylaması sona ermiştir.'
                },
                status=400
            )

        if submission.student == request.user:
            logger.warning(
                "Vote rejected: self-vote attempt. "
                "user_id=%s submission_id=%s",
                request.user.id,
                submission.id
            )

            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Kendi tasarımınıza oy veremezsiniz.'
                },
                status=400
            )

        already_voted = submission.voters.filter(
            id=request.user.id
        ).exists()

        if already_voted:
            logger.info(
                "Vote rejected: already voted. "
                "user_id=%s submission_id=%s",
                request.user.id,
                submission.id
            )

            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Bu tasarıma zaten oy verdiniz.'
                },
                status=400
            )

        current_vote_count = (
            competition.submissions
            .filter(
                voters=request.user
            )
            .count()
        )

        if current_vote_count >= MAX_VOTES_PER_COMPETITION:
            logger.warning(
                "Vote rejected: vote limit reached. "
                "user_id=%s competition_id=%s vote_count=%s",
                request.user.id,
                competition.id,
                current_vote_count
            )

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

        submission.voters.add(request.user)

        current_vote_count += 1

        remaining_votes = max(
            MAX_VOTES_PER_COMPETITION - current_vote_count,
            0
        )

        logger.info(
            "Vote successful. "
            "user_id=%s submission_id=%s competition_id=%s",
            request.user.id,
            submission.id,
            competition.id
        )

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

    except Exception:
        logger.exception(
            "Unexpected error while processing vote. "
            "user_id=%s submission_id=%s",
            request.user.id,
            submission_id
        )

        raise