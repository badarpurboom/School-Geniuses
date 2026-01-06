from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
import uuid
import random
import qrcode
from io import BytesIO
from django.core.files import File
from decimal import Decimal
from simple_history.models import HistoricalRecords

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ClassRoom(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)
    subjects = models.ManyToManyField(Subject, related_name="classes")

    def __str__(self):
        return f"{self.name} - {self.section}"
    
class ClassSubject(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('classroom', 'subject')

    def __str__(self):
        return f"{self.classroom} → {self.subject}"
    
class TimeTable(models.Model):
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day = models.CharField(
        max_length=20,
        choices=[
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
            ('Saturday', 'Saturday'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    teacher_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.classroom} | {self.subject} | {self.day}"

# --------Staff Table--------
class Staff(models.Model):
    ROLE_CHOICES = [
        ("Teacher", "Teacher"),
        ("Principal", "Principal"),
        ("Security Guard", "Security Guard"),
        ("Cleaner", "Cleaner"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=120)
    father_name = models.CharField(max_length=120, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    gender = models.CharField(max_length=10)
    dob = models.DateField()

    aadhaar = models.CharField(max_length=20, null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)

    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    joining_date = models.DateField()

    remarks = models.TextField(null=True, blank=True)

    # ------------- File Upload -------------
    document = models.FileField(upload_to="staff_docs/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
# --------Staff Table--------end


# Student table
class Student(models.Model):
    name = models.CharField(max_length=120)
    gender = models.CharField(max_length=10)

    dob = models.DateField()
    admission_date = models.DateField()

    student_class = models.CharField(max_length=20)
    section = models.CharField(max_length=10)

    father_name = models.CharField(max_length=120, null=True, blank=True)
    father_phone = models.CharField(max_length=15, null=True, blank=True)

    mother_name = models.CharField(max_length=120, null=True, blank=True)
    mother_phone = models.CharField(max_length=15, null=True, blank=True)

    address = models.TextField(null=True, blank=True)

    remarks = models.TextField(null=True, blank=True)

    document = models.FileField(upload_to="student_docs/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # --- Naye Fields ---
    student_id = models.CharField(max_length=9, null=True, blank=True, unique=False) # Fixed 9 digit ID
    roll_number = models.IntegerField(null=True, blank=True) # Serial wise (Changeable)
    qr_code = models.ImageField(upload_to="student_qrs/", null=True, blank=True)
    
    # Is line ko yahan likhein, ye upar ke saare fields ko track karega
    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        # 1. Generate Unique 9-digit Student ID (sirf pehli baar)
        if not self.student_id:
            while True:
                new_id = str(random.randint(100000000, 999999999))
                if not Student.objects.filter(student_id=new_id).exists():
                    self.student_id = new_id
                    break

        # 2. Generate Serial Roll Number (Agar nahi diya hai toh)
        if not self.roll_number:
            last_student = Student.objects.filter(
                student_class=self.student_class, 
                section=self.section
            ).order_by('-roll_number').first()
            
            if last_student and last_student.roll_number:
                self.roll_number = last_student.roll_number + 1
            else:
                self.roll_number = 1

        # 3. Generate QR Code containing Student ID
        if not self.qr_code:
            qr_image = qrcode.make(self.student_id)
            canvas = BytesIO()
            qr_image.save(canvas, format='PNG')
            fname = f'qr-{self.student_id}.png'
            self.qr_code.save(fname, File(canvas), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ID: {self.student_id} - Roll: {self.roll_number}"
# ----------Student table----------------------- end


@receiver(m2m_changed, sender=ClassRoom.subjects.through)
def create_class_subjects(sender, instance, action, pk_set, **kwargs):
    # Only when subjects are added
    if action == "post_add":
        from .models import ClassSubject, Subject
        
        for subject_id in pk_set:
            subject = Subject.objects.get(pk=subject_id)

            # Avoid duplicate entries
            ClassSubject.objects.get_or_create(
                classroom=instance,
                subject=subject
            )


# models.py
# api/models.py ke niche ye add karein
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, default="Present")

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student.name} - {self.date}"


class FeeStructure(models.Model):
    CLASS_CHOICES = [(str(i), f"Class {i}") for i in range(1, 13)] # 1 se 12 tak
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, unique=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Class {self.student_class} - ₹{self.monthly_fee}"

# 2. Student Fee Record: Kisne kitni fees di
class StudentFeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.CharField(max_length=20)
    year = models.IntegerField(default=2025)
    payment_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculation logic
        total = Decimal(str(self.total_fee))
        paid = Decimal(str(self.amount_paid))
        self.due_amount = total - paid
        
        # Safety check: Due negative nahi hona chahiye
        if self.due_amount < 0:
            self.due_amount = 0
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.month} ({self.year})"


class Exam(models.Model):
    exam_name = models.CharField(max_length=100) # e.g., Unit Test 1
    class_name = models.CharField(max_length=50) # e.g., Class 10
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_name} - {self.class_name}"

class ExamSchedule(models.Model):
    exam = models.ForeignKey(Exam, related_name='schedules', on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    exam_date = models.DateField()
    exam_time = models.TimeField()
    total_marks = models.IntegerField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.exam.exam_name} - {self.subject}"

# models.py mein ye add karein
class StudentMark(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks_obtained = models.FloatField()
    
    class Meta:
        # Taki ek student ka ek hi subject mein double entry na ho
        unique_together = ('student', 'exam', 'subject')
        

from django.db import models

class SchoolSettings(models.Model):
    name = models.CharField(max_length=255, default="My Cyber School")
    logo = models.ImageField(upload_to='school_logos/', null=True, blank=True)
    
    # --- Basic Contact Info ---
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    registration_no = models.CharField(max_length=100)
    
    # --- New Description Box ---
    description = models.TextField(
        null=True, 
        blank=True, 
        help_text="School ke baare mein detail yahan likhein (About Us section ke liye)."
    )

    class Meta:
        verbose_name_plural = "School General Settings"

    def save(self, *args, **kwargs):
        # Ye logic ensure karega ki database mein hamesha sirf EK hi record rahe
        if not self.pk and SchoolSettings.objects.exists():
            return 
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name