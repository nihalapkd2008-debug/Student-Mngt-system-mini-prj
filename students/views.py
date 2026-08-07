from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count
from .models import Student
from datetime import datetime, timedelta
import json
def dashboard(request):
    total_students = Student.objects.count()
    
    
    recent_students_count = Student.objects.all().order_by('-admission_date')[:10].count()
    
    distinct_classes = Student.objects.values('class_name').distinct().count()
    male_count = Student.objects.filter(gender='Male').count()
    female_count = Student.objects.filter(gender='Female').count()
    
    top_class_obj = Student.objects.values('class_name').annotate(count=Count('id')).order_by('-count').first()
    top_class_name = top_class_obj['class_name'] if top_class_obj else "N/A"
    
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        count = Student.objects.filter(admission_date=date).count()
        chart_labels.append(date.strftime('%a'))
        chart_data.append(count)
        
    recent_students = Student.objects.all().order_by('-admission_date')[:5]
    
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
    return render(request, 'dashboard.html', context)
def student_list(request):
    students = Student.objects.all().order_by('-id')
    return render(request, 'student_list.html', {'students': students})

def male_students(request):
    students = Student.objects.filter(gender='Male').order_by('-id')
    return render(request, 'student_list.html', {'students': students})

def female_students(request):
    students = Student.objects.filter(gender='Female').order_by('-id')
    return render(request, 'student_list.html', {'students': students})

# FIXED: RECENT now just shows the absolute latest 10, regardless of week
def recent_students(request):
    students = Student.objects.all().order_by('-admission_date')[:10]
    return render(request, 'student_list.html', {'students': students})

def top_class_list(request):
    top_class_obj = Student.objects.values('class_name').annotate(count=Count('id')).order_by('-count').first()
    top_class_name = top_class_obj['class_name'] if top_class_obj else "N/A"
    
    if top_class_name != "N/A":
        students = Student.objects.filter(class_name=top_class_name).order_by('-id')
    else:
        students = Student.objects.none()
        
    return render(request, 'student_list.html', {'students': students})

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
        if not name: errors.append("Name is required.")
        if not age or not age.isdigit() or int(age) <= 0: errors.append("Valid Age is required.")
        if not class_name: errors.append("Class is required.")
        if not phone or len(phone) < 10: errors.append("Valid Phone number is required (min 10 digits).")
        if not email: errors.append("Email is required.")
        if not admission_date: errors.append("Admission Date is required.")
        if Student.objects.filter(email=email).exists():
            errors.append("A student with this email already exists.")

        if errors:
            return render(request, 'add_student.html', {'errors': errors})

        Student.objects.create(
            name=name, age=int(age), gender=gender, class_name=class_name,
            phone=phone, email=email, address=address, admission_date=admission_date
        )
        messages.success(request, 'Student Added Successfully!')
        return redirect('student_list')

    return render(request, 'add_student.html')

def update_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if Student.objects.filter(email=new_email).exclude(id=student_id).exists():
            messages.error(request, "Email already in use by another student.")
            return render(request, 'update_student.html', {'student': student})

        student.name = request.POST.get('name')
        student.age = request.POST.get('age')
        student.gender = request.POST.get('gender')
        student.class_name = request.POST.get('class_name')
        student.phone = request.POST.get('phone')
        student.email = new_email
        student.address = request.POST.get('address')
        student.admission_date = request.POST.get('admission_date')
        student.save()
        messages.success(request, 'Student Updated Successfully!')
        return redirect('student_list')
    return render(request, 'update_student.html', {'student': student})

def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, 'Student Deleted Successfully!')
    return redirect('student_list')

def search_students(request):
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            Q(name__icontains=query) | 
            Q(phone__icontains=query) | 
            Q(email__icontains=query) |
            Q(class_name__icontains=query) |
            Q(gender__icontains=query)
        )
    else:
        students = Student.objects.all()
    data = [{'id': s.id, 'name': s.name, 'age': s.age, 'gender': s.gender, 
             'class': s.class_name, 'phone': s.phone, 'email': s.email, 
             'address': s.address, 'admission_date': str(s.admission_date)} for s in students]
    return JsonResponse({'students': data})