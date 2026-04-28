from django.contrib import admin
from .models import UserProfile, Field, FarmProject, FarmTask, FarmTaskProgressUpdate, FieldRecord

# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Field)
admin.site.register(FarmProject)
admin.site.register(FarmTask)
admin.site.register(FarmTaskProgressUpdate)
admin.site.register(FieldRecord)
