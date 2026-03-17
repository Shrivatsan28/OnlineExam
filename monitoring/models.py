from django.db import models
from accounts.models import CustomUser
from exams.models import Exam

class MonitoringLog(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='monitoring_logs')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50) # Only tab_switch is actively used now
    details = models.TextField()

    def __str__(self):
        return f"{self.student.username} - {self.event_type} - {self.timestamp}"

class AlertCounter(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    alert_count = models.PositiveIntegerField(default=0)
    is_auto_submitted = models.BooleanField(default=False)
    submission_reason = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.username} - Alerts: {self.alert_count}"
