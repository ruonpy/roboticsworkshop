from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import StudentProject, Badge, StudentBadge


class LikeProjectTests(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='testpassword123'
        )

        self.liker = User.objects.create_user(
            username='student2',
            password='testpassword123'
        )

        self.project = StudentProject.objects.create(
            title='Test Projesi',
            student=self.student,
            project_type='python',
            description='Test projesi açıklaması'
        )

    def test_like_project_success(self):
        """
        When a user likes a project:
        - Like should be recorded
        - like_count should increase by 1
        - Liker should gain +2 XP
        - Project owner should gain +10 XP
        """

        self.client.login(
            username='student2',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'like_project',
                args=[self.project.id]
            )
        )

        self.assertEqual(response.status_code, 200)

        self.project.refresh_from_db()

        self.assertEqual(self.project.like_count, 1)

        self.assertTrue(
            self.project.liked_by.filter(
                id=self.liker.id
            ).exists()
        )

        self.liker.profile.refresh_from_db()
        self.student.profile.refresh_from_db()

        self.assertEqual(
            self.liker.profile.exp,
            2
        )

        self.assertEqual(
            self.student.profile.exp,
            60
        )

    def test_cannot_like_same_project_twice(self):
        """
        The same user cannot like the same project a second time.
        """

        self.client.login(
            username='student2',
            password='testpassword123'
        )

        # First like
        first_response = self.client.post(
            reverse(
                'like_project',
                args=[self.project.id]
            )
        )

        self.assertEqual(
            first_response.status_code,
            200
        )

        # Second like
        second_response = self.client.post(
            reverse(
                'like_project',
                args=[self.project.id]
            )
        )

        self.assertEqual(
            second_response.status_code,
            400
        )

        self.project.refresh_from_db()

        # Like count must remain 1
        self.assertEqual(
            self.project.like_count,
            1
        )

        # XP should not be awarded twice
        self.liker.profile.refresh_from_db()
        self.student.profile.refresh_from_db()

        self.assertEqual(
            self.liker.profile.exp,
            2
        )

        self.assertEqual(
            self.student.profile.exp,
            60
        )

    def test_unauthenticated_user_cannot_like(self):
        """
        An unauthenticated user cannot like a project.
        """

        response = self.client.post(
            reverse(
                'like_project',
                args=[self.project.id]
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.project.refresh_from_db()

        self.assertEqual(
            self.project.like_count,
            0
        )

    def test_user_can_like_another_project(self):
        """
        A user can like multiple different projects.
        """

        second_project = StudentProject.objects.create(
            title='İkinci Test Projesi',
            student=self.student,
            project_type='scratch',
            description='İkinci test projesi'
        )

        self.client.login(
            username='student2',
            password='testpassword123'
        )

        response1 = self.client.post(
            reverse(
                'like_project',
                args=[self.project.id]
            )
        )

        response2 = self.client.post(
            reverse(
                'like_project',
                args=[second_project.id]
            )
        )

        self.assertEqual(
            response1.status_code,
            200
        )

        self.assertEqual(
            response2.status_code,
            200
        )

        self.project.refresh_from_db()
        second_project.refresh_from_db()

        self.assertEqual(
            self.project.like_count,
            1
        )

        self.assertEqual(
            second_project.like_count,
            1
        )

        self.liker.profile.refresh_from_db()

        # Two different likes → 2 + 2 XP
        self.assertEqual(
            self.liker.profile.exp,
            4
        )
    def test_team_player_badge_at_5_different_likes(self):
        """
        A user should earn the Team Player badge
        after liking 5 different projects.
        """

        team_player = Badge.objects.create(
            code='team_player',
            title='Takım Oyuncusu',
            description='5 farklı projeyi beğen.',
            icon_class='fa-users',
            badge_color='#3B82F6'
        )

        projects = []

        # Create 5 different projects
        for i in range(5):
            project = StudentProject.objects.create(
                title=f'Test Projesi {i + 1}',
                student=self.student,
                project_type='python',
                description=f'Test açıklaması {i + 1}'
            )

            projects.append(project)

        self.client.login(
            username='student2',
            password='testpassword123'
        )

        # Like 5 different projects
        for project in projects:
            response = self.client.post(
                reverse(
                    'like_project',
                    args=[project.id]
                )
            )

            self.assertEqual(
                response.status_code,
                200
            )

        # User should have liked 5 different projects
        self.assertEqual(
            self.liker.liked_projects.count(),
            5
        )

        # Team Player badge should be awarded
        self.assertTrue(
            StudentBadge.objects.filter(
                student=self.liker,
                badge=team_player
            ).exists()
        )

        # Badge should only exist once
        self.assertEqual(
            StudentBadge.objects.filter(
                student=self.liker,
                badge=team_player
            ).count(),
            1
        )

    def test_support_star_badge_at_25_different_likes(self):
        """
        A user should earn the Support Star badge
        after liking 25 different projects.
        """

        support_star = Badge.objects.create(
            code='support_star',
            title='Destek Yıldızı',
            description='25 farklı projeyi beğen.',
            icon_class='fa-star',
            badge_color='#FFD700'
        )

        projects = []

        # Create 25 different projects
        for i in range(25):
            project = StudentProject.objects.create(
                title=f'Test Projesi {i + 1}',
                student=self.student,
                project_type='python',
                description=f'Test açıklaması {i + 1}'
            )

            projects.append(project)

        self.client.login(
            username='student2',
            password='testpassword123'
        )

        # Like 24 projects first
        for project in projects[:24]:
            response = self.client.post(
                reverse(
                    'like_project',
                    args=[project.id]
                )
            )

            self.assertEqual(
                response.status_code,
                200
            )

        # 24 likes should NOT be enough
        self.assertEqual(
            self.liker.liked_projects.count(),
            24
        )

        self.assertFalse(
            StudentBadge.objects.filter(
                student=self.liker,
                badge=support_star
            ).exists()
        )

        # Like the 25th different project
        response = self.client.post(
            reverse(
                'like_project',
                args=[projects[24].id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        # User should now have 25 different likes
        self.assertEqual(
            self.liker.liked_projects.count(),
            25
        )

        # Support Star badge should be awarded
        self.assertTrue(
            StudentBadge.objects.filter(
                student=self.liker,
                badge=support_star
            ).exists()
        )

        # Badge should only exist once
        self.assertEqual(
            StudentBadge.objects.filter(
                student=self.liker,
                badge=support_star
            ).count(),
            1
        )