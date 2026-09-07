from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Student, Fee, Attendance
from .forms import StudentForm, FeeForm
from datetime import datetime, timedelta
import json
from django.utils import timezone

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import StudentSerializer


# =========================================================
# LOGIN
# =========================================================

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# =========================================================
# REGISTER
# =========================================================

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(
            request,
            'Registration successful. Please login.'
        )

        return redirect('login')

    return render(request, 'register.html')


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')

    return redirect('dashboard')


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):
    total_students = Student.objects.count()

    recent_students_count = (
        Student.objects.all()
        .order_by('-admission_date')[:10]
        .count()
    )

    distinct_classes = (
        Student.objects
        .values('class_name')
        .distinct()
        .count()
    )

    male_count = Student.objects.filter(
        gender='Male'
    ).count()

    female_count = Student.objects.filter(
        gender='Female'
    ).count()

    top_class_obj = (
        Student.objects
        .values('class_name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    top_class_name = (
        top_class_obj['class_name']
        if top_class_obj
        else "N/A"
    )

    # Chart data - Last 7 days
    chart_labels = []
    chart_data = []

    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)

        count = Student.objects.filter(
            admission_date=date
        ).count()

        chart_labels.append(
            date.strftime('%a')
        )

        chart_data.append(count)

    recent_students = (
        Student.objects
        .all()
        .order_by('-admission_date')[:5]
    )

    context = {
        'total_students': total_students,
        'recent_students_count': recent_students_count,
        'distinct_classes': distinct_classes,
        'male_count': male_count,
        'female_count': female_count,
        'top_class_name': top_class_name,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'recent_students': recent_students,
    }

    return render(
        request,
        'dashboard.html',
        context
    )


# =========================================================
# STUDENT LIST
# =========================================================

@login_required
def student_list(request):
    students = (
        Student.objects
        .all()
        .order_by('-id')
    )

    return render(
        request,
        'student_list.html',
        {'students': students}
    )


# =========================================================
# MALE STUDENTS
# =========================================================

@login_required
def male_students(request):
    students = (
        Student.objects
        .filter(gender='Male')
        .order_by('-id')
    )

    return render(
        request,
        'student_list.html',
        {'students': students}
    )


# =========================================================
# FEMALE STUDENTS
# =========================================================

@login_required
def female_students(request):
    students = (
        Student.objects
        .filter(gender='Female')
        .order_by('-id')
    )

    return render(
        request,
        'student_list.html',
        {'students': students}
    )


# =========================================================
# RECENT STUDENTS
# =========================================================

@login_required
def recent_students(request):
    students = (
        Student.objects
        .all()
        .order_by('-admission_date')[:10]
    )

    return render(
        request,
        'student_list.html',
        {'students': students}
    )


# =========================================================
# TOP CLASS STUDENTS
# =========================================================

@login_required
def top_class_list(request):
    top_class_obj = (
        Student.objects
        .values('class_name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    top_class_name = (
        top_class_obj['class_name']
        if top_class_obj
        else "N/A"
    )

    if top_class_name != "N/A":
        students = (
            Student.objects
            .filter(class_name=top_class_name)
            .order_by('-id')
        )
    else:
        students = Student.objects.none()

    return render(
        request,
        'student_list.html',
        {'students': students}
    )


# =========================================================
# ADD STUDENT
# =========================================================

@login_required
def add_student(request):
    if request.method == 'POST':

        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        class_name = request.POST.get('class_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        admission_date = request.POST.get('admission_date')

        errors = []

        if not name:
            errors.append("Name is required.")

        if (
            not age
            or not age.isdigit()
            or int(age) <= 0
        ):
            errors.append(
                "Valid Age is required."
            )

        if not class_name:
            errors.append(
                "Class is required."
            )

        if not phone or len(phone) < 10:
            errors.append(
                "Valid Phone number is required (min 10 digits)."
            )

        if not email:
            errors.append(
                "Email is required."
            )

        if not admission_date:
            errors.append(
                "Admission Date is required."
            )

        if Student.objects.filter(
            email=email
        ).exists():
            errors.append(
                "A student with this email already exists."
            )

        if errors:
            return render(
                request,
                'add_student.html',
                {'errors': errors}
            )

        Student.objects.create(
            name=name,
            age=int(age),
            gender=gender,
            class_name=class_name,
            phone=phone,
            email=email,
            address=address,
            admission_date=admission_date
        )

        messages.success(
            request,
            'Student Added Successfully!'
        )

        return redirect('student_list')

    return render(
        request,
        'add_student.html'
    )


# =========================================================
# UPDATE STUDENT
# =========================================================

@login_required
def update_student(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    if request.method == 'POST':

        new_email = request.POST.get('email')

        if (
            Student.objects
            .filter(email=new_email)
            .exclude(id=student_id)
            .exists()
        ):
            messages.error(
                request,
                "Email already in use by another student."
            )

            return render(
                request,
                'update_student.html',
                {'student': student}
            )

        student.name = request.POST.get('name')
        student.age = request.POST.get('age')
        student.gender = request.POST.get('gender')
        student.class_name = request.POST.get('class_name')
        student.phone = request.POST.get('phone')
        student.email = new_email
        student.address = request.POST.get('address')
        student.admission_date = request.POST.get('admission_date')

        student.save()

        messages.success(
            request,
            'Student Updated Successfully!'
        )

        return redirect('student_list')

    return render(
        request,
        'update_student.html',
        {'student': student}
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@login_required
def delete_student(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    if request.method == 'POST':
        student.delete()

        messages.success(
            request,
            'Student Deleted Successfully!'
        )

        return redirect('student_list')

    return redirect('student_list')


# =========================================================
# SEARCH STUDENTS
# =========================================================

@login_required
def search_students(request):

    query = request.GET.get('q', '')

    if query:
        students = Student.objects.filter(
            Q(name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
            | Q(class_name__icontains=query)
            | Q(gender__icontains=query)
        )
    else:
        students = Student.objects.all()

    data = [
        {
            'id': s.id,
            'name': s.name,
            'age': s.age,
            'gender': s.gender,
            'class': s.class_name,
            'phone': s.phone,
            'email': s.email,
            'address': s.address,
            'admission_date': str(s.admission_date)
        }
        for s in students
    ]

    return JsonResponse({
        'students': data
    })


# =========================================================
# STUDENT PROFILE
# =========================================================

@login_required
def student_profile(request, student_id):

    student = get_object_or_404(
        Student,
        id=student_id
    )

    # Fees
    fees = student.fees.all()

    # Attendance
    present_count = (
        student.attendances
        .filter(status='Present')
        .count()
    )

    absent_count = (
        student.attendances
        .filter(status='Absent')
        .count()
    )

    leave_count = (
        student.attendances
        .filter(status='Leave')
        .count()
    )

    # For display
    attendances = student.attendances.all()[:30]

    # Fee calculations
    total_fees = (
        fees.aggregate(Sum('amount'))['amount__sum']
        or 0
    )

    paid_fees = (
        fees
        .filter(status='Paid')
        .aggregate(Sum('amount'))['amount__sum']
        or 0
    )

    pending_fees = total_fees - paid_fees

    context = {
        'student': student,
        'fees': fees,
        'attendances': attendances,
        'total_fees': total_fees,
        'paid_fees': paid_fees,
        'pending_fees': pending_fees,
        'present_count': present_count,
        'absent_count': absent_count,
        'leave_count': leave_count,
    }

    return render(
        request,
        'student_profile.html',
        context
    )


# =========================================================
# FEE MANAGEMENT
# =========================================================

@login_required
def fee_list(request):

    fees = (
        Fee.objects
        .all()
        .select_related('student')
    )

    status_filter = request.GET.get(
        'status',
        ''
    )

    if status_filter:
        fees = fees.filter(
            status=status_filter
        )

    student_filter = request.GET.get(
        'student',
        ''
    )

    if student_filter:
        fees = fees.filter(
            student__name__icontains=student_filter
        )

    total_amount = (
        fees.aggregate(Sum('amount'))['amount__sum']
        or 0
    )

    paid_amount = (
        fees
        .filter(status='Paid')
        .aggregate(Sum('amount'))['amount__sum']
        or 0
    )

    pending_amount = (
        fees
        .filter(status='Pending')
        .aggregate(Sum('amount'))['amount__sum']
        or 0
    )

    overdue_amount = (
        fees
        .filter(status='Overdue')
        .aggregate(Sum('amount'))['amount__sum']
        or 0
    )

    context = {
        'fees': fees,
        'total_amount': total_amount,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'overdue_amount': overdue_amount,
        'status_filter': status_filter,
    }

    return render(
        request,
        'fee_list.html',
        context
    )


# =========================================================
# ADD FEE
# =========================================================

@login_required
def add_fee(request):

    if request.method == 'POST':

        student_id = request.POST.get('student')
        amount = request.POST.get('amount')
        fee_date = request.POST.get('fee_date')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status')
        description = request.POST.get(
            'description',
            ''
        )

        student = get_object_or_404(
            Student,
            id=student_id
        )

        Fee.objects.create(
            student=student,
            amount=amount,
            fee_date=fee_date,
            due_date=due_date,
            status=status,
            description=description
        )

        messages.success(
            request,
            'Fee record added successfully! 💰'
        )

        return redirect('fee_list')

    students = Student.objects.all()

    return render(
        request,
        'add_fee.html',
        {'students': students}
    )


# =========================================================
# UPDATE FEE
# =========================================================

@login_required
def update_fee(request, fee_id):

    fee = get_object_or_404(
        Fee,
        id=fee_id
    )

    if request.method == 'POST':

        student_id = request.POST.get('student')
        amount = request.POST.get('amount')
        fee_date = request.POST.get('fee_date')
        due_date = request.POST.get('due_date')
        status = request.POST.get('status')
        description = request.POST.get(
            'description',
            ''
        )

        fee.student = get_object_or_404(
            Student,
            id=student_id
        )

        fee.amount = amount
        fee.fee_date = fee_date
        fee.due_date = due_date
        fee.status = status
        fee.description = description

        fee.save()

        messages.success(
            request,
            'Fee record updated successfully! ✅'
        )

        return redirect('fee_list')

    students = Student.objects.all()

    return render(
        request,
        'add_fee.html',
        {
            'fee': fee,
            'students': students
        }
    )


# =========================================================
# DELETE FEE
# =========================================================

@login_required
def delete_fee(request, fee_id):

    fee = get_object_or_404(
        Fee,
        id=fee_id
    )

    if request.method == 'POST':
        fee.delete()

        messages.success(
            request,
            'Fee record deleted! 🗑️'
        )

        return redirect('fee_list')

    return redirect('fee_list')


# =========================================================
# ATTENDANCE MANAGEMENT
# =========================================================

@login_required
def attendance_list(request):

    attendances = (
        Attendance.objects
        .all()
        .select_related('student')
    )

    date_filter = request.GET.get(
        'date',
        ''
    )

    if date_filter:
        attendances = attendances.filter(
            date=date_filter
        )

    status_filter = request.GET.get(
        'status',
        ''
    )

    if status_filter:
        attendances = attendances.filter(
            status=status_filter
        )

    student_filter = request.GET.get(
        'student',
        ''
    )

    if student_filter:
        attendances = attendances.filter(
            student__name__icontains=student_filter
        )

    today = timezone.now().date()

    today_attendance = Attendance.objects.filter(
        date=today
    )

    present_today = today_attendance.filter(
        status='Present'
    ).count()

    absent_today = today_attendance.filter(
        status='Absent'
    ).count()

    leave_today = today_attendance.filter(
        status='Leave'
    ).count()

    context = {
        'attendances': attendances,
        'present_today': present_today,
        'absent_today': absent_today,
        'leave_today': leave_today,
        'date_filter': date_filter,
        'status_filter': status_filter,
    }

    return render(
        request,
        'attendance_list.html',
        context
    )


# =========================================================
# MARK ATTENDANCE
# =========================================================

@login_required
def mark_attendance(request):

    if request.method == 'POST':

        student_ids = request.POST.getlist(
            'student_id'
        )

        date = request.POST.get(
            'date',
            str(timezone.now().date())
        )

        for student_id in student_ids:

            status = request.POST.get(
                f'status_{student_id}'
            )

            if status:

                student = get_object_or_404(
                    Student,
                    id=student_id
                )

                attendance, created = (
                    Attendance.objects.get_or_create(
                        student=student,
                        date=date,
                        defaults={
                            'status': status
                        }
                    )
                )

                if not created:
                    attendance.status = status
                    attendance.save()

        messages.success(
            request,
            'Attendance marked successfully! ✅'
        )

        return redirect('attendance_list')

    students = Student.objects.all()

    today = timezone.now().date()

    attendance_data = []

    for student in students:

        att = Attendance.objects.filter(
            student=student,
            date=today
        ).first()

        attendance_data.append({
            'student': student,
            'attendance': att,
        })

    context = {
        'attendance_data': attendance_data,
        'today': today,
    }

    return render(
        request,
        'mark_attendance.html',
        context
    )


# =========================================================
# STUDENT API - VIEWSET
# =========================================================

class StudentViewSet(ModelViewSet):

    queryset = Student.objects.all()

    serializer_class = StudentSerializer