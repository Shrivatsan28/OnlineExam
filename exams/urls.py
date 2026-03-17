from django.urls import path
from . import views

urlpatterns = [
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/create-exam/', views.create_exam, name='create_exam'),
    path('staff/add-question/<int:exam_id>/', views.add_question, name='add_question'),
    path('staff/allocate-students/<int:exam_id>/', views.allocate_students, name='allocate_students'),
    path('staff/questions/<int:exam_id>/', views.view_questions, name='view_questions'),
    path('staff/edit-question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('staff/delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    path('staff/exam-results/<int:exam_id>/', views.view_exam_results, name='view_exam_results'),
    path('staff/edit-exam/<int:exam_id>/', views.edit_exam, name='edit_exam'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/enroll/<int:exam_id>/', views.enroll_exam, name='enroll_exam'),
    path('student/result/<int:result_id>/', views.view_result, name='view_result'),
    path('student/take-exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('student/submit-exam/<int:exam_id>/', views.submit_exam, name='submit_exam'),
]
