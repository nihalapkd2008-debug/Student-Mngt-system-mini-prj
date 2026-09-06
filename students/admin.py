from django.contrib import admin
from .models import Student, Fee, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_name', 'gender', 'phone', 'is_active']
    search_fields = ['name', 'phone', 'email']
    list_filter = ['class_name', 'gender', 'is_active']

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'amount', 'fee_date', 'due_date', 'status']
    list_filter = ['status']
    search_fields = ['student__name']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status']
    list_filter = ['status', 'date']
    search_fields = ['student__name']