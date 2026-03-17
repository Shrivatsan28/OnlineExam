from django.urls import path
from . import views

urlpatterns = [
    path('log-event/', views.log_monitoring_event, name='log_monitoring_event'),
    path('logs/', views.view_monitoring_logs, name='view_logs_all'),
    path('logs/exam/<int:exam_id>/', views.view_monitoring_logs, name='view_logs_exam'),
]
