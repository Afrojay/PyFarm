from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from .forms import FieldForm, FarmProjectForm, FarmTaskForm, FarmTaskCompletionForm, FieldRecordForm
from .models import FarmProject, FarmTask, FieldRecord, UserProfile


def get_user_role(user):
    if not user.is_authenticated:
        return None

    try:
        return user.userprofile.role
    except UserProfile.DoesNotExist:
        return None


def user_has_role(user, *roles):
    return get_user_role(user) in roles


def require_role(request, *roles):
    if user_has_role(request.user, *roles):
        return True

    messages.error(request, "Your role does not have permission to do that.")
    return False


def home(request):
    projects = FarmProject.objects.all()
    tasks = FarmTask.objects.prefetch_related("progress_updates")
    field_records = FieldRecord.objects.select_related("field", "project", "created_by")

    user_role = get_user_role(request.user)
    user_role_display = None
    if request.user.is_authenticated and user_role:
        user_role_display = request.user.userprofile.get_role_display()

    return render(request, "tracker/home.html", {
        "projects": projects,
        "tasks": tasks,
        "field_records": field_records,
        "user_role": user_role,
        "user_role_display": user_role_display,
        "can_plan_work": user_has_role(request.user, UserProfile.FARM_MANAGER),
        "can_complete_tasks": user_has_role(request.user, UserProfile.FIELD_WORKER),
        "can_create_field_records": user_has_role(request.user, UserProfile.AGRONOMIST),
    })

def project_detail(request, project_id):
    project = get_object_or_404(FarmProject, id=project_id)
    tasks = project.tasks.prefetch_related("progress_updates")
    field_records = project.field_records.select_related("field", "created_by")

    return render(request, "tracker/project_detail.html", {
        "project": project,
        "tasks": tasks,
        "field_records": field_records,
        "can_complete_tasks": user_has_role(request.user, UserProfile.FIELD_WORKER),
        "can_create_field_records": user_has_role(request.user, UserProfile.AGRONOMIST),
    })


def task_detail(request, task_id):
    task = get_object_or_404(
        FarmTask.objects.select_related("project", "assigned_to").prefetch_related(
            "progress_updates__updated_by"
        ),
        id=task_id,
    )

    return render(request, "tracker/task_detail.html", {
        "task": task,
        "can_complete_tasks": (
            task.status != "DONE"
            and user_has_role(request.user, UserProfile.FIELD_WORKER)
            and task.assigned_to == request.user
        ),
    })


@login_required
def create_field(request):
    if not require_role(request, UserProfile.FARM_MANAGER):
        return redirect("home")

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
    if not require_role(request, UserProfile.FARM_MANAGER):
        return redirect("home")

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
    if not require_role(request, UserProfile.FARM_MANAGER):
        return redirect("home")

    if request.method == "POST":
        form = FarmTaskForm(request.POST, request.FILES)
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
def update_task_progress(request, task_id):
    if not require_role(request, UserProfile.FIELD_WORKER):
        return redirect("home")

    task = get_object_or_404(FarmTask, id=task_id, assigned_to=request.user)

    if request.method == "POST":
        form = FarmTaskCompletionForm(request.POST, request.FILES)
        if form.is_valid():
            progress_update = form.save(commit=False)
            progress_update.task = task
            progress_update.updated_by = request.user
            progress_update.save()

            task.status = progress_update.status
            task.progress_comment = progress_update.comment
            if progress_update.image:
                task.image = progress_update.image
            task.save()
            return redirect("home")
    else:
        form = FarmTaskCompletionForm(initial={
            "status": task.status if task.status != "TODO" else "IN_PROGRESS",
            "comment": task.progress_comment,
        })

    return render(request, "tracker/form.html", {
        "form": form,
        "title": f"Update Task Progress: {task.title}",
    })


@login_required
def create_field_record(request):
    if not require_role(request, UserProfile.AGRONOMIST):
        return redirect("home")

    if request.method == "POST":
        form = FieldRecordForm(request.POST)
        if form.is_valid():
            field_record = form.save(commit=False)
            field_record.created_by = request.user
            field_record.save()
            return redirect("home")
    else:
        form = FieldRecordForm()

    return render(request, "tracker/form.html", {
        "form": form,
        "title": "Create Field Record",
    })
