from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date

from .models import UserProfile, Field, FarmProject, FarmTask


class PyFarmModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="manager",
            email="manager@pyfarm.com",
            password="password"
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
            role="FARM_MANAGER"
        )

        self.field = Field.objects.create(
            name="North Field",
            crop_type="Potatoes",
            size_acres=5.5,
            location="Main Farm"
        )

        self.project = FarmProject.objects.create(
            title="Spring Planting Plan",
            description="Plan for preparing and planting the north field.",
            field=self.field,
            manager=self.user,
            start_date=date(2026, 4, 1),
            end_date=date(2026, 5, 1),
            status="PLANNED"
        )

        self.task = FarmTask.objects.create(
            project=self.project,
            title="Prepare soil",
            description="Clear weeds and prepare the soil before planting.",
            assigned_to=self.user,
            due_date=date(2026, 4, 5),
            status="TODO",
            priority="HIGH"
        )

    def test_project_string_returns_title(self):
        self.assertEqual(str(self.project), "Spring Planting Plan")

    def test_task_is_linked_to_project(self):
        self.assertEqual(self.task.project, self.project)

    def test_user_profile_role(self):
        self.assertEqual(self.profile.role, "FARM_MANAGER")


class PyFarmViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="manager",
            email="manager@pyfarm.com",
            password="password"
        )

        self.field = Field.objects.create(
            name="East Field",
            crop_type="Carrots",
            size_acres=3.0,
            location="Back Farm"
        )

        self.project = FarmProject.objects.create(
            title="Carrot Growing Project",
            description="Project for growing carrots.",
            field=self.field,
            manager=self.user,
            start_date=date(2026, 4, 10),
            end_date=date(2026, 6, 10),
            status="IN_PROGRESS"
        )

        self.task = FarmTask.objects.create(
            project=self.project,
            title="Water seedlings",
            description="Water the carrot seedlings.",
            assigned_to=self.user,
            due_date=date(2026, 4, 15),
            status="TODO",
            priority="MEDIUM"
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PyFarm")

    def test_project_detail_page_loads(self):
        response = self.client.get(reverse("project_detail", args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carrot Growing Project")

    def test_create_project_requires_login(self):
        response = self.client.get(reverse("create_project"))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_mark_task_done(self):
        self.client.login(username="manager", password="password")
        response = self.client.get(reverse("mark_task_done", args=[self.task.id]))

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.status, "DONE")