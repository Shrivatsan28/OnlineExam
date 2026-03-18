from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .decorators import role_required
from .models import CustomUser, StudentProfile, StaffProfile
from .forms import StudentSignUpForm, StaffCreationForm, StudentEditForm, StaffEditForm
from django.contrib import messages
from monitoring.models import MonitoringLog
from exams.models import Exam
from .email_utils import send_student_email
import datetime

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'home.html')
    if request.user.is_admin():
        return redirect('admin_dashboard')
    elif request.user.role == 'STAFF':
        return redirect('staff_dashboard')
    else:
        return redirect('student_dashboard')

def student_signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = StudentSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form, 'role': 'Student'})

def user_login(request, role_expected=None):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if role_expected and user.role != role_expected and not user.is_superuser:
                    return render(request, 'accounts/login.html', {
                        'form': form, 
                        'error': f'Invalid login for {role_expected} role.'
                    })
                login(request, user)

                # ── Email: Login Alert (students only) ──────────────────────
                if user.role == 'STUDENT' and user.email:
                    now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
                    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
                    send_student_email(
                        subject="🔔 Login Alert – Invigilo Exam System",
                        message=(
                            f"Hello {user.get_full_name() or user.username},\n\n"
                            f"A new login was detected on your Invigilo account.\n\n"
                            f"  Username : {user.username}\n"
                            f"  Time     : {now_ist.strftime('%d %b %Y, %I:%M %p')} IST\n"
                            f"  IP       : {ip}\n\n"
                            f"If this wasn't you, please contact your exam administrator immediately.\n\n"
                            f"Invigilo Exam System"
                        ),
                        recipient_email=user.email,
                    )

                if user.is_admin():
                    return redirect('admin_dashboard')
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form, 'role': role_expected})

def user_logout(request):
    logout(request)
    return redirect('login')

@role_required(['ADMIN'])
def admin_dashboard(request):
    data = {
        'total_students': CustomUser.objects.filter(role='STUDENT', is_superuser=False).count(),
        'total_staff': CustomUser.objects.filter(role='STAFF', is_superuser=False).count(),
        'total_exams': Exam.objects.count(),
        'recent_logs': MonitoringLog.objects.all().order_by('-timestamp')[:10],
    }
    return render(request, 'accounts/admin_dashboard.html', data)

@role_required(['ADMIN'])
def manage_staff(request):
    staff_members = CustomUser.objects.filter(role='STAFF', is_superuser=False).prefetch_related('staff_profile')
    if request.method == 'POST':
        form = StaffCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member created successfully.')
            return redirect('manage_staff')
    else:
        form = StaffCreationForm()
    
    return render(request, 'accounts/manage_staff.html', {
        'staff_members': staff_members,
        'form': form
    })

@role_required(['ADMIN'])
def delete_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, id=staff_id, role='STAFF', is_superuser=False)
    staff.delete()
    messages.success(request, 'Staff member deleted successfully.')
    return redirect('manage_staff')

@role_required(['ADMIN'])
def edit_staff(request, staff_id):
    staff = get_object_or_404(CustomUser, id=staff_id, role='STAFF', is_superuser=False)
    if request.method == 'POST':
        form = StaffEditForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f'Staff member "{staff.username}" updated successfully.')
            return redirect('manage_staff')
    else:
        form = StaffEditForm(instance=staff)
    return render(request, 'accounts/edit_staff.html', {'form': form, 'staff': staff})

@role_required(['ADMIN', 'STAFF'])
def manage_students(request):
    students = CustomUser.objects.filter(role='STUDENT', is_superuser=False).prefetch_related('student_profile')
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student created successfully.')
            return redirect('manage_students')
    else:
        form = StudentSignUpForm()
    
    back_url = 'admin_dashboard' if request.user.is_admin() else 'staff_dashboard'
    return render(request, 'accounts/manage_students.html', {
        'students': students,
        'form': form,
        'back_url': back_url,
    })

@role_required(['ADMIN', 'STAFF'])
def delete_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role='STUDENT', is_superuser=False)
    student.delete()
    messages.success(request, 'Student deleted successfully.')
    return redirect('manage_students')

@role_required(['ADMIN', 'STAFF'])
def edit_student(request, student_id):
    student = get_object_or_404(CustomUser, id=student_id, role='STUDENT', is_superuser=False)
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student "{student.username}" updated successfully.')
            return redirect('manage_students')
    else:
        form = StudentEditForm(instance=student)
    return render(request, 'accounts/edit_student.html', {'form': form, 'student': student})
