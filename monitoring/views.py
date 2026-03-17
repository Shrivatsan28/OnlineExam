from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser
from exams.models import Exam, Result
from .models import MonitoringLog, AlertCounter
import json
from accounts.decorators import role_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@csrf_exempt
@role_required(['STUDENT'])
def log_monitoring_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event_type = data.get('event_type', '').lower()

        # Strictly only store tab_switch events
        if event_type != 'tab_switch':
            return JsonResponse({'status': 'ignored'})

        exam_id   = data.get('exam_id')
        details   = data.get('details', '')
        exam      = get_object_or_404(Exam, id=exam_id)

        # Save the log entry
        MonitoringLog.objects.create(
            student=request.user,
            exam=exam,
            event_type=event_type,
            details=details
        )

        # ── Violation path ────────────────────────────────────────────────────
        counter, _ = AlertCounter.objects.get_or_create(student=request.user, exam=exam)
        counter.alert_count += 1
        auto_submit = False

        if counter.alert_count >= 3:
            counter.is_auto_submitted = True
            counter.submission_reason = f"Auto-submitted due to 3+ violations: {event_type}"
            auto_submit = True

            # Email staff once, on exactly the 3rd violation
            if counter.alert_count == 3:
                staff = exam.created_by
                if staff and staff.email:
                    try:
                        send_mail(
                            subject=f'\u26a0 Cheating Alert: {request.user.get_full_name() or request.user.username} \u2014 {exam.title}',
                            message=(
                                f'Cheating detected during exam.\n\n'
                                f'Student  : {request.user.get_full_name() or request.user.username} (@{request.user.username})\n'
                                f'Exam     : {exam.title}\n'
                                f'Violation: {event_type}\n'
                                f'Time     : {timezone.now().strftime("%d %b %Y %H:%M:%S")}\n\n'
                                f'The student has accumulated 3 or more violations and will be auto-failed.'
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[staff.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        print(f"Failed to send cheating alert email: {e}")

        counter.save()
        return JsonResponse({
            'status': 'success',
            'alert_count': counter.alert_count,
            'auto_submit': auto_submit
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@role_required(['ADMIN', 'STAFF'])
def view_monitoring_logs(request, exam_id=None):
    if exam_id:
        logs = MonitoringLog.objects.filter(exam_id=exam_id).order_by('-timestamp')
    else:
        logs = MonitoringLog.objects.all().order_by('-timestamp')
    return render(request, 'monitoring/logs.html', {'logs': logs})
