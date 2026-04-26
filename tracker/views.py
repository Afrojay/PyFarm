from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FarmProject, FarmTask, Field
from .forms import FieldForm, FarmProjectForm, FarmTaskForm


def home(request):
    projects = FarmProject.objects.all()
    tasks = FarmTask.objects.all()

    return render(request, "tracker/home.html", {
        "projects": projects,
        "tasks": tasks,
    })

@login_required
def create_field(request):
    if request.method == "POST":
        form = FieldForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = FieldForm()

    return render(request, "tracker/form.html", {
        "form": form,
        "title": "Add Field",
    })

@login_required
def create_project(request):
    if request.method == "POST":
        form = FarmProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            return redirect("home")
    else:
        form = FarmProjectForm()

    return render(request, "tracker/form.html", {
        "form": form,
        "title": "Create Project",
    })


@login_required
def create_task(request):
    if request.method == "POST":
        form = FarmTaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = FarmTaskForm()

    return render(request, "tracker/form.html", {
        "form": form,
        "title": "Create Task",
    })

@login_required
def mark_task_done(request, task_id):
    task = get_object_or_404(FarmTask, id=task_id)
    task.status = "DONE"
    task.save()
    return redirect("home")