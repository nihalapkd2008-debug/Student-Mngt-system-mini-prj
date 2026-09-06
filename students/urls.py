from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Students
    path('students/', views.student_list, name='student_list'),
    path('api/students/', views.student_api, name='student_api'),
    path('add/', views.add_student, name='add_student'),
    path('update/<int:student_id>/', views.update_student, name='update_student'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('api/search/', views.search_students, name='search_students'),
    path('students/male/', views.male_students, name='male_students'),
    path('students/female/', views.female_students, name='female_students'),
    path('students/recent/', views.recent_students, name='recent_students'),
    path('students/top-class/', views.top_class_list, name='top_class_list'),
    
    # Profile
    path('profile/<int:student_id>/', views.student_profile, name='student_profile'),
    
    # Fees
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/add/', views.add_fee, name='add_fee'),
    path('fees/delete/<int:fee_id>/', views.delete_fee, name='delete_fee'),
    path('fees/update/<int:fee_id>/', views.update_fee, name='update_fee'),
    
    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
]