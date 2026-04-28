from .models import UserProfile


def navigation_roles(request):
    user = request.user
    role = None
    role_display = None

    if user.is_authenticated:
        try:
            profile = user.userprofile
            role = profile.role
            role_display = profile.get_role_display()
        except UserProfile.DoesNotExist:
            pass

    return {
        "nav_user_role": role,
        "nav_user_role_display": role_display,
        "nav_can_plan_work": role == UserProfile.FARM_MANAGER,
        "nav_can_complete_tasks": role == UserProfile.FIELD_WORKER,
        "nav_can_create_field_records": role == UserProfile.AGRONOMIST,
    }
