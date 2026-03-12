# myapp/Urls/Consultant_urls.py
from django.urls import path
from myapp.Views.Consultant_views import (
    consultant_create_student,
    consultant_update_student,
    consultant_list_students
)

urlpatterns = [
    path('consultant/students/', consultant_list_students, name="consultant_list_students"),
    path('consultant/students/create/', consultant_create_student, name="consultant_create_student"),
    path('consultant/students/<int:student_id>/update/', consultant_update_student, name="consultant_update_student"),
]