from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, StudentProfile, StaffProfile

class StudentSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    enrollment_number = forms.CharField(max_length=20, required=True)
    phone = forms.CharField(max_length=15, required=False)
    department = forms.CharField(max_length=100, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = 'STUDENT'
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                enrollment_number=self.cleaned_data['enrollment_number'],
                phone=self.cleaned_data['phone'],
                department=self.cleaned_data['department']
            )
        return user

class StaffCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    employee_id = forms.CharField(max_length=20, required=True)
    department = forms.CharField(max_length=100, required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'STAFF'
        if commit:
            user.save()
            StaffProfile.objects.create(
                user=user,
                employee_id=self.cleaned_data['employee_id'],
                department=self.cleaned_data['department']
            )
        return user

class StaffEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    employee_id = forms.CharField(max_length=20, required=True)
    phone = forms.CharField(max_length=15, required=False)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'staff_profile'):
            try:
                profile = self.instance.staff_profile
                self.fields['employee_id'].initial = profile.employee_id
                self.fields['phone'].initial = profile.phone
                self.fields['department'].initial = profile.department
            except StaffProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = StaffProfile.objects.get_or_create(
                user=user, defaults={'employee_id': user.username}
            )
            profile.employee_id = self.cleaned_data.get('employee_id', profile.employee_id)
            profile.phone = self.cleaned_data.get('phone', '')
            profile.department = self.cleaned_data.get('department', '')
            profile.save()
        return user

class StudentEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    department = forms.CharField(max_length=100, required=False)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'student_profile'):
            try:
                profile = self.instance.student_profile
                self.fields['phone'].initial = profile.phone
                self.fields['department'].initial = profile.department
            except StudentProfile.DoesNotExist:
                pass

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = StudentProfile.objects.get_or_create(
                user=user, defaults={'enrollment_number': user.username}
            )
            profile.phone = self.cleaned_data.get('phone', '')
            profile.department = self.cleaned_data.get('department', '')
            profile.save()
        return user
