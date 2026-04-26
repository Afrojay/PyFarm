from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("fields/new/", views.create_field, name="create_field"),
    path("projects/new/", views.create_project, name="create_project"),
    path("tasks/new/", views.create_task, name="create_task"),
    path("tasks/<int:task_id>/done/", views.mark_task_done, name="mark_task_done"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
]