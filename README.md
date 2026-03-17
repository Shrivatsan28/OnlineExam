# Online Exam Cheating Detection System

A robust, production-ready Django application for conducting online exams with built-in per-question timing and high-concurrency optimizations.

## 🚀 Key Features

- **Per-Question 60s Timer**: Every question has its own 60-second countdown. It auto-advances on expiry and auto-submits on the last question.
- **High-Concurrency Performance**: Optimized for **120+ simultaneous users** without lag:
  - **DB Connection Pooling**: Reuses database connections to reduce overhead.
  - **GZip Compression**: Drains less bandwidth by compressing server responses.
  - **Cached Sessions**: Faster authentication checks using a memory-backed session engine.
- **Cheating Detection**:
  - **Tab-Switch Monitoring**: Automatically logs when a student leaves the exam tab.
  - **Auto-Submission**: Exams are auto-submitted after 3 violations.
  - **Staff Email Alerts**: Real-time notifications to staff when cheating is detected.
- **Role-Based Access Control**:
  - **Admin**: Full system control, user management.
  - **Staff**: Create exams, manage questions, view results and logs.
  - **Student**: Take allocated exams, view results.

## 🛠 Setup & Installation

### 1. Prerequisites
- Python 3.12+
- PostgreSQL

### 2. Database Setup
1. Create a PostgreSQL database named `online_exam_db`.
2. Ensure the PostgreSQL service is running on your machine.

### 3. Installation
```powershell
# Clone the repository
cd project-OnlineExam

# Install dependencies
pip install django psycopg2-binary
```

### 4. Configuration
The application is pre-configured in `online_exam_ai/settings.py` for high performance. 
Ensure your DB credentials match:
- **DB Name**: `online_exam_db`
- **User**: `postgres`
- **Password**: `Shri@2803`

### 5. Running the Application
```powershell
# Apply migrations
python manage.py migrate

# Create a superuser (Admin)
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

## 📈 Performance Notes
The system is architected to handle **120+ concurrent PCs** by minimizing database transactions per second. The live monitoring grid has been removed in favor of a lean, event-driven logging system that only processes critical "tab-switch" events, ensuring the server stays responsive under heavy load.
