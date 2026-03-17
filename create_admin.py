import os
from django.contrib.auth import get_user_model

User = get_user_model()
admin_password = os.environ.get('ADMIN_PASSWORD', 'OnlineExamAdminSecret2026!')

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', admin_password)
    print(f"Superuser 'admin' created successfully.")
    print(f"PASSWORD HAS BEEN SET. If you didn't provide ADMIN_PASSWORD, the default is: {admin_password}")
else:
    # Update password if admin exists but we provided a new one in ENV
    if 'ADMIN_PASSWORD' in os.environ:
        admin = User.objects.get(username='admin')
        admin.set_password(admin_password)
        admin.save()
        print("Superuser 'admin' password updated to match ADMIN_PASSWORD variable.")
    else:
        print("Superuser 'admin' already exists.")
