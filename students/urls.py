from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('students/', views.student_list, name='student_list'),
    path('add/', views.add_student, name='add_student'),
    path('update/<int:student_id>/', views.update_student, name='update_student'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('api/search/', views.search_students, name='search_students'),
    path('students/male/', views.male_students, name='male_students'),
    path('students/female/', views.female_students, name='female_students'),
    path('students/recent/', views.recent_students, name='recent_students'),
    path('students/top-class/', views.top_class_list, name='top_class_list'),
        # <-- ADD THIS LINE
]