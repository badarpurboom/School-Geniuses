from django.urls import path
from .views import class_wise_income, create_subject, staff_list,subject_list,create_class,get_class_subjects,save_timetable,get_class_subjects,promote_students
from . import views
from .views import create_staff, create_student
from .views import ai_db_query

urlpatterns = [
    path("subjects/create/", create_subject),
    path('subjects/', subject_list),
    path("class/create/", create_class),
    path("classes/", views.get_classes),
    path("class-subjects/<int:class_id>/", views.get_class_subjects),
    path("save-timetable/", views.save_timetable),
    path("timetable/<int:class_id>/<str:day>/", views.get_timetable),
    path("staff/create/", create_staff),
    path("staff/", staff_list),
    path("teachers/", views.get_teachers),
    path("students/create/", create_student),
    path("ai-db-query/", ai_db_query),
    path('mark-attendance/', views.mark_attendance, name='mark-attendance'),
    path('get-fee/<str:student_id>/', views.get_student_fee_details),
    path('save-fee/', views.save_fee_payment),
    path('students/', views.get_student_list, name='get_student_list'),
    path('students/promote/', views.promote_students, name='promote_students'),
    path('exams/create-bulk/', views.create_exam_bulk, name='create-exam-bulk'),
    path('exams/', views.get_exams, name='get-exams'),
    path('marks/save-bulk/', views.save_marks_bulk, name='save-marks-bulk'),
    path('login/', views.login_view, name='login'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
    path("dashboard/today-attendance/", views.today_attendance_summary,name="today-attendance-summary"),
    path("dashboard/class-income/", views.class_wise_income,name="class-wise-income"),
    # path('whatsapp/', views.whatsapp_webhook, name='whatsapp_webhook'),


]
