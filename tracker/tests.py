from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UserProfile, Field, FarmProject, FarmTask, FarmTaskProgressUpdate, FieldRecord


class PyFarmModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="manager",
            email="manager@pyfarm.com",
            password="password"
        )

        self.profile = UserProfile.objects.create(
            user=self.user,
            role=UserProfile.FARM_MANAGER
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
            assigned_to=None,
            due_date=date(2026, 4, 5),
            status="TODO",
            priority="HIGH"
        )

    def test_project_string_returns_title(self):
        self.assertEqual(str(self.project), "Spring Planting Plan")

    def test_task_is_linked_to_project(self):
        self.assertEqual(self.task.project, self.project)

    def test_user_profile_role(self):
        self.assertEqual(self.profile.role, UserProfile.FARM_MANAGER)


class PyFarmViewTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager",
            email="manager@pyfarm.com",
            password="password"
        )
        UserProfile.objects.create(user=self.manager, role=UserProfile.FARM_MANAGER)

        self.worker = User.objects.create_user(
            username="worker",
            email="worker@pyfarm.com",
            password="password"
        )
        UserProfile.objects.create(user=self.worker, role=UserProfile.FIELD_WORKER)

        self.agronomist = User.objects.create_user(
            username="agronomist",
            email="agronomist@pyfarm.com",
            password="password"
        )
        UserProfile.objects.create(user=self.agronomist, role=UserProfile.AGRONOMIST)

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
            manager=self.manager,
            start_date=date(2026, 4, 10),
            end_date=date(2026, 6, 10),
            status="IN_PROGRESS"
        )

        self.task = FarmTask.objects.create(
            project=self.project,
            title="Water seedlings",
            description="Water the carrot seedlings.",
            assigned_to=self.worker,
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

    def test_task_detail_page_loads(self):
        FarmTaskProgressUpdate.objects.create(
            task=self.task,
            updated_by=self.worker,
            status="IN_PROGRESS",
            comment="Watering has started.",
        )

        response = self.client.get(reverse("task_detail", args=[self.task.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Water seedlings")
        self.assertContains(response, "Progress History")
        self.assertContains(response, "Watering has started.")

    def test_create_project_requires_login(self):
        response = self.client.get(reverse("create_project"))
        self.assertEqual(response.status_code, 302)

    def test_farm_manager_can_create_planning_records(self):
        self.client.login(username="manager", password="password")
        response = self.client.post(reverse("create_project"), {
            "title": "Second Carrot Project",
            "description": "Follow-up carrot work.",
            "field": self.field.id,
            "start_date": "2026-04-20",
            "end_date": "2026-06-20",
            "status": "PLANNED",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(FarmProject.objects.filter(title="Second Carrot Project").exists())

    def test_field_worker_can_open_complete_task_form(self):
        self.client.login(username="worker", password="password")
        response = self.client.get(reverse("update_task_progress", args=[self.task.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Update Task Progress")

    def test_field_worker_can_update_task_in_progress_without_image(self):
        self.client.login(username="worker", password="password")
        response = self.client.post(reverse("update_task_progress", args=[self.task.id]), {
            "status": "IN_PROGRESS",
            "comment": "I have started watering the first rows.",
        })

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.status, "IN_PROGRESS")
        self.assertEqual(self.task.progress_comment, "I have started watering the first rows.")
        self.assertFalse(self.task.image)
        self.assertTrue(FarmTaskProgressUpdate.objects.filter(
            task=self.task,
            updated_by=self.worker,
            status="IN_PROGRESS",
            comment="I have started watering the first rows.",
        ).exists())

    def test_field_worker_can_upload_optional_image_and_mark_task_done(self):
        self.client.login(username="worker", password="password")
        image = SimpleUploadedFile(
            "task.gif",
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )
        response = self.client.post(reverse("update_task_progress", args=[self.task.id]), {
            "status": "DONE",
            "comment": "Finished watering all seedlings.",
            "image": image,
        })

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.status, "DONE")
        self.assertEqual(self.task.progress_comment, "Finished watering all seedlings.")
        self.assertTrue(self.task.image)
        self.assertTrue(FarmTaskProgressUpdate.objects.filter(
            task=self.task,
            updated_by=self.worker,
            status="DONE",
            comment="Finished watering all seedlings.",
        ).exists())

    def test_farm_manager_cannot_mark_task_done(self):
        self.client.login(username="manager", password="password")
        response = self.client.get(reverse("update_task_progress", args=[self.task.id]))

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.task.status, "TODO")

    def test_field_worker_cannot_update_task_assigned_to_someone_else(self):
        other_worker = User.objects.create_user(
            username="otherworker",
            email="otherworker@pyfarm.com",
            password="password"
        )
        UserProfile.objects.create(user=other_worker, role=UserProfile.FIELD_WORKER)

        self.client.login(username="otherworker", password="password")
        response = self.client.post(reverse("update_task_progress", args=[self.task.id]), {
            "status": "DONE",
            "comment": "Trying to update another worker's task.",
        })

        self.task.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.task.status, "TODO")
        self.assertFalse(FarmTaskProgressUpdate.objects.exists())

    def test_agronomist_can_create_field_record(self):
        self.client.login(username="agronomist", password="password")
        response = self.client.post(reverse("create_field_record"), {
            "field": self.field.id,
            "project": self.project.id,
            "crop": "Carrots",
            "crop_stage": "Seedling",
            "advice": "Keep soil evenly moist.",
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(FieldRecord.objects.filter(crop="Carrots").exists())

    def test_field_worker_cannot_create_field_record(self):
        self.client.login(username="worker", password="password")
        response = self.client.post(reverse("create_field_record"), {
            "field": self.field.id,
            "project": self.project.id,
            "crop": "Carrots",
            "crop_stage": "Seedling",
            "advice": "Keep soil evenly moist.",
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(FieldRecord.objects.exists())


class PyFarmFixtureTests(TestCase):
    def test_demo_fixture_loads(self):
        call_command("loaddata", "pyfarm_data", verbosity=0)

        self.assertTrue(User.objects.filter(username="manager").exists())
        self.assertTrue(Field.objects.exists())
        self.assertTrue(FarmProject.objects.exists())
        self.assertTrue(FarmTask.objects.exists())
        self.assertTrue(FarmTaskProgressUpdate.objects.exists())
        self.assertTrue(FieldRecord.objects.exists())
        self.assertTrue(self.client.login(username="manager", password="password"))
