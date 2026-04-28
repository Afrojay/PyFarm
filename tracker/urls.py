from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("fields/new/", views.create_field, name="create_field"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    path("projects/new/", views.create_project, name="create_project"),
    path("tasks/<int:task_id>/", views.task_detail, name="task_detail"),
    path("tasks/new/", views.create_task, name="create_task"),
    path("tasks/<int:task_id>/progress/", views.update_task_progress, name="update_task_progress"),
    path("field-records/new/", views.create_field_record, name="create_field_record"),

]
