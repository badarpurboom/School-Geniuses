from turtle import st
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ClassRoom, Subject,ClassSubject,TimeTable,Staff, Student,Attendance,FeeStructure, StudentFeePayment,Exam,StudentMark
from .langchain_service import ask_sql
from datetime import date
import re
from decimal import Decimal
from rest_framework import status
from .serializers import ExamSerializer
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.db.models import Count, Sum

import os
from django.http import HttpResponse
# from .langchain_service import ask_database  # Aapka existing service
import requests

@csrf_exempt
def create_subject(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name")

        if not name:
            return JsonResponse(
                {"error": "Subject name required"},
                status=400
            )

        subject, created = Subject.objects.get_or_create(name=name)

        return JsonResponse({
            "id": subject.id,
            "name": subject.name,
            "created": created
        })
    
def subject_list(request):
    subjects = Subject.objects.all().values("id", "name")
    return JsonResponse(list(subjects), safe=False)

@csrf_exempt
def create_class(request):
    if request.method == "POST":
        data = json.loads(request.body)

        name = data.get("name")
        section = data.get("section")
        subject_ids = data.get("subjects", [])

        classroom = ClassRoom.objects.create(
            name=name,
            section=section
        )

        subjects = Subject.objects.filter(id__in=subject_ids)
        classroom.subjects.set(subjects)

        return JsonResponse({
            "message": "Class created successfully",
            "class": f"{name}-{section}"
        })


@api_view(['GET'])
def get_class_subjects(request, class_id):
    subjects = ClassSubject.objects.filter(classroom_id=class_id)
    data = [
        {
            "id": cs.subject.id,
            "name": cs.subject.name
        }
        for cs in subjects
    ]
    return Response(data)

# start-----------— COMPLETE & WORKING (Dynamic Time Table APIs)
# GET ALL CLASSES--
@api_view(["GET"])
def get_classes(request):
    classes = ClassRoom.objects.all()

    data = []

    for c in classes:
        data.append({
            "id": c.id,
            "name": c.name,
            "section": c.section
        })

    return Response(data)
# and--GET ALL CLASSES--


# start--GET CLASS SUBJECTS--
@api_view(['GET'])
def get_class_subjects(request, class_id):
    class_subjects = ClassSubject.objects.filter(classroom_id=class_id)

    data = []
    for cs in class_subjects:
        data.append({
            "class_subject_id": cs.id,        # 🔥 MOST IMPORTANT
            "subject_name": cs.subject.name
        })

    return Response(data)
# and--GET CLASS SUBJECTS--

# start--SAVE TIME TABLE--
@api_view(["POST"])
def save_timetable(request):
    data = request.data

    class_id = data.get("class_id")
    day = data.get("day")
    periods = data.get("periods")

    if not class_id or not day or not periods:
        return Response({"error": "Missing data"}, status=400)

    try:
        classroom = ClassRoom.objects.get(id=class_id)
    except ClassRoom.DoesNotExist:
        return Response({"error": "Class not found"}, status=404)

    # delete old timetable for that class + day
    TimeTable.objects.filter(classroom=classroom, day=day).delete()

    for p in periods:
        subject_name = p.get("subject")
        teacher_name = p.get("teacher") or ""

        try:
            subject = Subject.objects.get(name=subject_name)
        except Subject.DoesNotExist:
            return Response({"error": f"Subject '{subject_name}' not found"}, status=400)

        TimeTable.objects.create(
            classroom=classroom,
            subject=subject,
            day=day,
            start_time=p.get("time_from"),   # matches model
            end_time=p.get("time_to"),       # matches model
            teacher_name=teacher_name
        )

    return Response({"message": "Timetable saved successfully"})
# and--SAVE TIME TABLE--

# start--FETCH SAVED TIMETABLE (optional — edit view ke liye)--
@api_view(["GET"])
def get_timetable(request, class_id, day):
    rows = TimeTable.objects.filter(
        classroom_id=class_id,
        day=day
    ).order_by("period")

    data = []

    for r in rows:
        data.append({
            "period": r.period,
            "subject": r.subject.name,
            "teacher": r.teacher_name,
            "time_from": str(r.time_from),
            "time_to": str(r.time_to),
        })

    return Response(data)
# and--FETCH SAVED TIMETABLE (optional — edit view ke liye)--
# and-----------— COMPLETE & WORKING (Dynamic Time Table APIs)

@api_view(['GET'])
def get_student_list(request):
    class_id = request.query_params.get('class_id')
    
    if class_id:
        try:
            # 1. Pehle ID se Class ka naam dhoondo (e.g., 19 -> "10th")
            # Isse aapka CharField wala system disturb nahi hoga
            target_class = ClassRoom.objects.get(id=class_id)
            
            # 2. Ab Student table mein us naam se filter karo
            students = Student.objects.filter(student_class=target_class.name)
            
        except ClassRoom.DoesNotExist:
            return JsonResponse([], safe=False)
    else:
        students = Student.objects.all()
    
    student_list = []
    for s in students:
        student_list.append({
            "id": s.id,
            "name": s.name,
            "section": s.section 
        })
    
    return JsonResponse(student_list, safe=False)

@api_view(['POST'])
def promote_students(request):
    try:
        data = request.data
        student_ids = data.get('student_ids', [])
        target_class_id = data.get('target_class_id')
        target_section = data.get('target_section')

        target_class_obj = ClassRoom.objects.get(id=target_class_id)

        # Bulk Update ki jagah hum loop chalayenge
        students = Student.objects.filter(id__in=student_ids)
        
        for student in students:
            student.student_class = target_class_obj.name
            student.section = target_section
            # Yahan hum roll_number ko None kar denge taaki model ka save() naya generate kare
            student.roll_number = None 
            student.save() # Ab ye aapke model ka save() trigger karega

        return Response({"message": f"{students.count()} students promoted successfully"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

# --------for saving Staff------
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_staff(request):

    data = request.data

    staff = Staff.objects.create(
        name=data.get("name"),
        father_name=data.get("father_name"),
        phone=data.get("phone"),

        gender=data.get("gender"),
        dob=data.get("dob"),

        aadhaar=data.get("aadhaar"),
        marital_status=data.get("marital_status"),

        role=data.get("role"),
        joining_date=data.get("joining_date"),

        remarks=data.get("remarks"),
        document=request.FILES.get("document")  # file save
    )

    return Response({"message": "Staff created successfully", "id": staff.id})
# --------for saving Staff------end
# List Staff (for table view later)
@api_view(["GET"])
def staff_list(request):
    staff = Staff.objects.all().values()
    return Response(list(staff))
# List Staff (for table view later) end

# ------teachers list
@api_view(["GET"])
def get_teachers(request):
    teachers = Staff.objects.filter(role="Teacher").values("id", "name")
    return Response(list(teachers))
# ------teachers list end

# -----create_student----
@api_view(["POST"])
def create_student(request):
    data = request.data

    student = Student.objects.create(
        name=data.get("name"),
        gender=data.get("gender"),
        dob=data.get("dob"),
        admission_date=data.get("admission_date"),
        student_class=data.get("student_class"),
        section=data.get("section"),
        father_name=data.get("father_name"),
        father_phone=data.get("father_phone"),
        mother_name=data.get("mother_name"),
        mother_phone=data.get("mother_phone"),
        address=data.get("address"),
        remarks=data.get("remarks"),
    )

    # file upload (if any)
    if "document" in request.FILES:
        student.document = request.FILES["document"]
        student.save()

    return Response({"message": "Student added successfully!"})
# -----create_student----end


# langchain AI DB QUERY VIEW--
from .langchain_service import ask_sql

@api_view(["POST"])
def ai_db_query(request):
    user_query = request.data.get("query", "")

    if not user_query:
        return Response({"error": "Query empty!"}, status=400)

    try:
        answer = ask_sql(user_query)
        return Response({"answer": answer})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
# langchain AI DB QUERY VIEW--end


@api_view(['POST'])
def mark_attendance(request):
    s_id = str(request.data.get('student_id', '')).strip()
    # 1. Aaj ki date fix karo
    today = timezone.now().date()

    try:
        student = Student.objects.get(student_id=s_id)

        attendance, created = Attendance.objects.get_or_create(
            student=student, 
            date=today, # <-- YE LINE FIX KAREGI PROBLEM
            defaults={'status': 'Present'}
            )

        if created:
            message = "Attendance Marked"
        else:
            message = "Already Marked Today"

        return Response({
            "status": "success",
            "message": message,
            "name": student.name,   
            "class": student.student_class,
            "section": student.section,
            "roll": student.roll_number,
            "date": str(today)
        }, status=200)

    except Student.DoesNotExist:
        return Response({"status": "error", "message": "Student Not Found"}, status=404)
    except Exception as e:
        # Taki humein pata chale asli error kya hai
        return Response({"status": "error", "message": str(e)}, status=500)



@csrf_exempt # Taaki POST request block na ho
def get_student_fee_details(request, student_id):
    # Terminal mein print karein taaki humein dikhe request aayi
    print(f"Checking fees for ID: {student_id}") 
    
    clean_id = str(student_id).strip()
    try:
        student = Student.objects.get(student_id=clean_id)
        # ---- IMPORTANT FIX ----
        # Class string se sirf digits nikaal lo (ex: "Class 1 A" -> "1")
        import re
        class_number = re.findall(r'\d+', str(student.student_class))
        class_number = class_number[0] if class_number else student.student_class
        
        fee_structure = FeeStructure.objects.get(student_class=class_number)
        
        data = {
            "name": student.name,
            "class": student.student_class,
            "section": student.section,
            "roll": student.roll_number,
            "monthly_fee": float(fee_structure.monthly_fee),
            "status": "success"
        }
        return JsonResponse(data)
    except Student.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Student ID nahi mila"}, status=404)
    except FeeStructure.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Fees set nahi hai"}, status=404)



@csrf_exempt
def save_fee_payment(request):
    if request.method == "POST":
        try:
            # 1. Data load karna
            data = json.loads(request.body.decode('utf-8'))
            print(f"DEBUG DATA: {data}") # Terminal mein check karein data aa raha hai ya nahi

            s_id = str(data.get('student_id', '')).strip()
            if not s_id:
                return JsonResponse({"status": "error", "message": "Student ID missing"}, status=400)

            # 2. Student dhundo
            student = Student.objects.get(student_id=s_id)
            
            # 3. Fees Calculation (Safe Way)
            pure_class = str(student.student_class).strip()
            total = Decimal('0.00')

            # Pehle Database mein check karein
            fee_exists = FeeStructure.objects.filter(student_class=pure_class).first()
            if fee_exists:
                total = Decimal(str(fee_exists.monthly_fee))
            else:
                # Agar database mein nahi hai, toh UI wala use karein
                ui_fee = data.get('fixed_fee')
                if ui_fee is not None:
                    total = Decimal(str(ui_fee))
                else:
                    return JsonResponse({"status": "error", "message": f"Class {pure_class} ki fees kahi nahi mili!"}, status=400)

            # 4. Paid Amount
            paid_val = data.get('amount_paid', 0)
            paid = Decimal(str(paid_val))

            # 5. Save Record
            payment = StudentFeePayment.objects.create(
                student=student,
                total_fee=total,
                amount_paid=paid,
                month=data.get('month', 'January'),
                year=int(data.get('year', 2025))
            )

            return JsonResponse({
                "status": "success",
                "due": float(payment.due_amount)
            })

        except Student.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Student record not found"}, status=400)
        except Exception as e:
            import traceback
            print("--- TRACEBACK START ---")
            print(traceback.format_exc()) # Yeh terminal mein asli wajah batayega
            print("--- TRACEBACK END ---")
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "POST required"}, status=405)       




@api_view(['POST'])
def create_exam_bulk(request):
    if request.method == 'POST':
        # Streamlit se aane wale data ko rename karna pad sakta hai 
        # schedule -> schedules (serializer ke mutabiq)
        data = request.data
        if 'schedule' in data:
            # Keys ko frontend se backend match kar rahe hain
            for item in data['schedule']:
                item['exam_date'] = item.pop('date')
                item['exam_time'] = item.pop('time')
            
        serializer = ExamSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Exam Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_exams(request):
    exams = Exam.objects.all()
    serializer = ExamSerializer(exams, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def save_marks_bulk(request):
    data = request.data
    exam_id = data.get('exam_id')
    subject = data.get('subject')
    marks_list = data.get('marks_list') # Ye wo list hai jo Streamlit se aa rahi hai

    try:
        exam = Exam.objects.get(id=exam_id)
        for entry in marks_list:
            student = Student.objects.get(id=entry['student_id'])
            # update_or_create use kar rahe hain taaki agar marks dubara bhare jayein toh purane update ho jayein
            StudentMark.objects.update_or_create(
                student=student,
                exam=exam,
                subject=subject,
                defaults={'marks_obtained': entry['marks']}
            )
        return Response({"message": "Marks saved successfully"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    # 1. User verify karein
    user = authenticate(username=username, password=password)
    
    if user:
        # 2. Token generate karein
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username}, status=200)
    else:
        return Response({"error": "Galt details!"}, status=401)



@api_view(['GET'])
def dashboard_stats(request):
    total_students = Student.objects.count()
    total_staff = Staff.objects.count()
    
    # Aaj ki attendance ka count
    today = timezone.now().date()
    present_today = Attendance.objects.filter(date=today, status='Present').count()
    
    # Attendance Percentage calculate karein
    attendance_percent = 0
    if total_students > 0:
        attendance_percent = round((present_today / total_students) * 100, 1)

    return Response({
        "total_students": total_students,
        "total_staff": total_staff,
        "present_today": present_today,
        "attendance_percent": attendance_percent
    })
    
    
@api_view(['GET'])
def today_attendance_summary(request):
    today = date.today()
    # Student model se Class aur Section dono ka combination nikaalo
    # Isse humein [('Class 1', 'A'), ('Class 1', 'B'), ('Class 2', 'A')...] milega
    class_sections = Student.objects.values_list('student_class', 'section').distinct()
    
    response_list = []
    for cls, sec in class_sections:
        present = Attendance.objects.filter(
            student__student_class=cls, 
            student__section=sec,
            date=today, 
            status="Present"
        ).count()

        response_list.append({
            "class": cls,
            "section": sec,
            "present": present
        })

    return Response(response_list)

# 2CLASS-WISE FEE COLLECTION
@api_view(['GET'])
def class_wise_income(request):
    data = (
        StudentFeePayment.objects
        .values('student__student_class')
        .annotate(total_collected=Sum('amount_paid'))
        .order_by('student__student_class')
    )

    chart_data = [
        {
            "class": d['student__student_class'],
            "collected": float(d['total_collected'] or 0)
        }
        for d in data
    ]

    return Response(chart_data)




