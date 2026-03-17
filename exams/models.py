from django.db import models
from accounts.models import CustomUser

class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='exams_created')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    pass_marks = models.PositiveIntegerField()
    student_limit = models.PositiveIntegerField(default=30)
    total_questions = models.PositiveIntegerField(default=10)
    allocated_students = models.ManyToManyField(CustomUser, related_name='allocated_exams', blank=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    marks = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.exam.title} - {self.question_text[:50]}"

class Result(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    score = models.FloatField()
    total_questions = models.PositiveIntegerField()
    correct_answers = models.PositiveIntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('PASS', 'Pass'), ('FAIL', 'Fail'), ('CHEATING', 'Cheating')])

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} - {self.score}"
