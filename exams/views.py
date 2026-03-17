from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.decorators import role_required
from .models import Exam, Question, Result
from .forms import ExamForm, QuestionForm
from accounts.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings
from monitoring.models import MonitoringLog, AlertCounter

@role_required(['STAFF', 'ADMIN'])
def staff_dashboard(request):
    if request.user.is_admin():
        exams = Exam.objects.all()
    else:
        exams = Exam.objects.filter(created_by=request.user)
    return render(request, 'exams/staff_dashboard.html', {'exams': exams})

@role_required(['STAFF', 'ADMIN'])
def edit_exam(request, exam_id):
    if request.user.is_admin():
        exam = get_object_or_404(Exam, id=exam_id)
    else:
        exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, f'Exam "{exam.title}" updated successfully.')
            return redirect('staff_dashboard')
    else:
        form = ExamForm(instance=exam)
    return render(request, 'exams/edit_exam.html', {'form': form, 'exam': exam})


@role_required(['STAFF', 'ADMIN'])
def create_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            return redirect('add_question', exam_id=exam.id)
    else:
        form = ExamForm()
    return render(request, 'exams/create_exam.html', {'form': form})

@role_required(['STAFF', 'ADMIN'])
def add_question(request, exam_id):
    if request.user.is_admin():
        exam = get_object_or_404(Exam, id=exam_id)
    else:
        exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)

    current_count = exam.questions.count()
    total_required = exam.total_questions

    # Already at the limit — redirect away
    if current_count >= total_required:
        messages.success(request, f'All {total_required} questions have been added.')
        return redirect('staff_dashboard')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            current_count += 1

            if current_count >= total_required:
                messages.success(request, f'All {total_required} questions added successfully!')
                return redirect('staff_dashboard')

            if 'add_another' in request.POST:
                messages.info(request, f'Question {current_count} of {total_required} saved.')
                return redirect('add_question', exam_id=exam.id)

            # "Finalize" clicked but quota not met
            messages.error(request, f'You must add exactly {total_required} questions. Only {current_count} added so far.')
            return redirect('add_question', exam_id=exam.id)
    else:
        form = QuestionForm()

    return render(request, 'exams/add_question.html', {
        'form': form,
        'exam': exam,
        'current_count': current_count,
        'total_required': total_required,
        'remaining': total_required - current_count,
    })

@role_required(['STAFF', 'ADMIN'])
def allocate_students(request, exam_id):
    if request.user.is_admin():
        exam = get_object_or_404(Exam, id=exam_id)
    else:
        exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    students = CustomUser.objects.filter(role='STUDENT', is_superuser=False, is_staff=False)
    if request.method == 'POST':
        student_ids = request.POST.getlist('students')
        
        if len(student_ids) > exam.student_limit:
            messages.error(request, f"Cannot allocate {len(student_ids)} students. Maximum allowed is {exam.student_limit}.")
            return redirect('allocate_students', exam_id=exam.id)
            
        allocated_students = CustomUser.objects.filter(id__in=student_ids)
        exam.allocated_students.set(allocated_students)
        
        # Send Email notification
        for student in allocated_students:
            exam_url = request.build_absolute_uri(f'/exams/student/take-exam/{exam.id}/')
            subject = f"Exam Scheduled: {exam.title}"
            message = (
                f"Hello {student.get_full_name() or student.username},\n\n"
                f"You have been allocated to the exam: {exam.title}.\n\n"
                f"Start Time: {exam.start_time}\n"
                f"End Time: {exam.end_time}\n"
                f"Duration: {exam.duration_minutes} minutes\n\n"
                f"Click the link below to take your exam at the scheduled time:\n"
                f"{exam_url}\n\n"
                f"Good luck!"
            )
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [student.email])
            except Exception as e:
                print(f"Failed to send email to {student.email}: {e}")

        messages.success(request, f"Students allocated to {exam.title} and notifications sent.")
        return redirect('staff_dashboard')
    return render(request, 'exams/allocate_students.html', {'exam': exam, 'students': students})

@role_required(['STUDENT'])
def student_dashboard(request):
    # Get IDs of exams the student has already completed
    completed_exam_ids = Result.objects.filter(student=request.user).values_list('exam_id', flat=True)

    # Filter available exams to exclude completed ones
    available_exams = Exam.objects.filter(allocated_students=request.user).exclude(id__in=completed_exam_ids)

    # Show only the single latest result per exam (avoid duplicates from old data)
    seen_exams = set()
    unique_results = []
    for result in Result.objects.filter(student=request.user).order_by('-submitted_at'):
        if result.exam_id not in seen_exams:
            seen_exams.add(result.exam_id)
            unique_results.append(result)

    return render(request, 'exams/student_dashboard.html', {
        'available_exams': available_exams,
        'my_results': unique_results
    })

@role_required(['STUDENT'])
def enroll_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.user in exam.allocated_students.all():
        messages.info(request, "You are already enrolled for this exam.")
    else:
        exam.allocated_students.add(request.user)
        messages.success(request, f"Successfully enrolled for {exam.title}.")
    if request.user.is_admin():
        return redirect('admin_dashboard')
    return redirect('student_dashboard')

@role_required(['STUDENT'])
def view_result(request, result_id):
    result = get_object_or_404(Result, id=result_id, student=request.user)
    return render(request, 'exams/view_result.html', {'result': result})

@role_required(['STUDENT'])
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, allocated_students=request.user)
    questions = exam.questions.all()
    # Check if already submitted
    if Result.objects.filter(student=request.user, exam=exam).exists():
        messages.warning(request, "You have already submitted this exam.")
        return redirect('student_dashboard')
    
    return render(request, 'monitoring/take_exam.html', {
        'exam': exam,
        'questions': questions
    })

@role_required(['STUDENT'])
def submit_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id, allocated_students=request.user)

    # Block re-submission — one attempt per exam
    if Result.objects.filter(student=request.user, exam=exam).exists():
        messages.warning(request, "You have already submitted this exam.")
        return redirect('student_dashboard')

    if request.method == 'POST':
        questions = exam.questions.all()
        correct_count = 0
        for q in questions:
            selected_option = request.POST.get(f'question_{q.id}')
            if selected_option == q.correct_option:
                correct_count += 1
        
        score = (correct_count / questions.count()) * 100 if questions.count() > 0 else 0
        status = 'PASS' if score >= exam.pass_marks else 'FAIL'

        # --- Cheating Check ---
        # Count real violations (exclude HEARTBEAT)
        violation_count = MonitoringLog.objects.filter(
            student=request.user,
            exam=exam
        ).exclude(event_type__iexact='HEARTBEAT').count()

        # Also check AlertCounter
        try:
            alert_counter = AlertCounter.objects.get(student=request.user, exam=exam)
            total_alerts = alert_counter.alert_count
        except AlertCounter.DoesNotExist:
            total_alerts = 0

        CHEAT_THRESHOLD = 3  # fail if 3 or more real violations
        if violation_count >= CHEAT_THRESHOLD or total_alerts >= CHEAT_THRESHOLD:
            status = 'CHEATING'

        result = Result.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            total_questions=questions.count(),
            correct_answers=correct_count,
            status=status
        )
        
        # Send Result Email
        subject = f"Exam Result: {exam.title}"
        message = f"Hello {request.user.get_full_name() or request.user.username},\n\nYou have completed the exam: {exam.title}.\n\nYour Score: {score}%\nResult: {status}\n\nThank you for participating."
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email])
        except Exception as e:
            print(f"Failed to send result email to {request.user.email}: {e}")

        messages.success(request, f"Exam {exam.title} submitted successfully. Your score: {score}%")
        if request.user.is_admin():
            return redirect('admin_dashboard')
        return redirect('student_dashboard')
    return redirect('take_exam', exam_id=exam_id)


@role_required(['STAFF', 'ADMIN'])
def view_questions(request, exam_id):
    if request.user.is_admin():
        exam = get_object_or_404(Exam, id=exam_id)
    else:
        exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    questions = exam.questions.all()
    return render(request, 'exams/view_questions.html', {'exam': exam, 'questions': questions})

@role_required(['STAFF', 'ADMIN'])
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    # Security check: Admin can edit any, Staff only their own
    if not request.user.is_admin() and question.exam.created_by != request.user:
        messages.error(request, "You don't have permission to edit this question.")
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Question updated successfully.")
            return redirect('view_questions', exam_id=question.exam.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'exams/edit_question.html', {'form': form, 'question': question})

@role_required(['STAFF', 'ADMIN'])
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.exam.id
    # Security check
    if not request.user.is_admin() and question.exam.created_by != request.user:
        messages.error(request, "You don't have permission to delete this question.")
        return redirect('staff_dashboard')
    
    question.delete()
    messages.success(request, "Question deleted successfully.")
    return redirect('view_questions', exam_id=exam_id)


@role_required(['STAFF', 'ADMIN'])
def view_exam_results(request, exam_id):
    if request.user.is_admin():
        exam = get_object_or_404(Exam, id=exam_id)
    else:
        # Ensure the staff member created the exam
        exam = get_object_or_404(Exam, id=exam_id, created_by=request.user)
    
    # Deduplicate: show only the latest result per student
    seen_students = set()
    unique_results = []
    for result in Result.objects.filter(exam=exam).order_by('student_id', '-submitted_at'):
        if result.student_id not in seen_students:
            seen_students.add(result.student_id)
            unique_results.append(result)

    # Sort by score descending for a leaderboard view
    unique_results.sort(key=lambda r: r.score, reverse=True)

    return render(request, 'exams/view_exam_results.html', {'exam': exam, 'results': unique_results})

