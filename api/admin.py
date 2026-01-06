from django.contrib import admin
from .models import Subject, ClassRoom, ClassSubject,TimeTable,Staff, Student, Attendance,FeeStructure, StudentFeePayment,Exam, ExamSchedule, StudentMark,SchoolSettings
from import_export.admin import ImportExportModelAdmin

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

# admin.site.register(ClassRoom)
@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'section')
    actions = ["copy_subjects_to_other_sections"]

    def copy_subjects_to_other_sections(self, request, queryset):
        from .models import ClassSubject, ClassRoom, Subject

        count = 0

        for classroom in queryset:
            # Same class ke saare sections (except current)
            other_sections = ClassRoom.objects.filter(
                name=classroom.name
            ).exclude(id=classroom.id)

            # Current class ke subjects
            subjects = ClassSubject.objects.filter(classroom=classroom)

            for other in other_sections:
                for cs in subjects:
                    # Duplicate ko avoid karo
                    ClassSubject.objects.get_or_create(
                        classroom=other,
                        subject=cs.subject
                    )
                    # ManyToMany bhi sync kar dete hain
                    other.subjects.add(cs.subject)

                count += 1

        self.message_user(
            request,
            f"🎯 Subjects successfully copied to {count} class/sections!"
        )

    copy_subjects_to_other_sections.short_description = (
        "📚 Copy selected class subjects → other sections of same class"
    )


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ('id',"classroom", "subject")
    list_filter = ("classroom",)

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('id',
        "classroom",
        "subject",
        "day",
        "start_time",
        "end_time",
        "teacher_name"
    )
    list_filter = ("classroom", "day")

@admin.register(Staff)
class StaffAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'role')

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):   
    list_display = ('id', 'name', 'student_class', 'section')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    # Attendance list mein kya dikhega
    list_display = ('get_student_name', 'get_student_class', 'date', 'status')
    
    # Filter by Date and Class
    list_filter = ('date', 'student__student_class', 'status')
    
    # Student ke naam se search karne ke liye
    search_fields = ('student__name', 'student__student_id')

    # Custom functions to show student details in Attendance list
    def get_student_name(self, obj):
        return obj.student.name
    get_student_name.short_description = 'Student Name'

    def get_student_class(self, obj):
        return f"{obj.student.student_class} - {obj.student.section}"
    get_student_class.short_description = 'Class'


admin.site.register(FeeStructure)
admin.site.register(StudentFeePayment)



# 1. Exam ke andar hi Schedule dikhe uske liye Inline setup
class ExamScheduleInline(admin.TabularInline):
    model = ExamSchedule
    extra = 1

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'class_name', 'created_at')
    inlines = [ExamScheduleInline]

# 2. Marks ko register karna taaki table dikhe
@admin.register(StudentMark)
class StudentMarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'subject', 'marks_obtained')
    list_filter = ('exam', 'subject', 'student') # Side mein filter aa jayenge
    search_fields = ('student__name', 'subject') # Search bar kaam karega
    
    
    
@admin.register(SchoolSettings)
class SchoolSettingsAdmin(admin.ModelAdmin):
    # Admin panel ki list mein kya dikhega
    list_display = ('name', 'email', 'contact_number', 'registration_no')
    
    # Form ko sections mein divide karne ke liye (Fieldsets)
    fieldsets = (
        ("School Identity", {
            'fields': ('name', 'logo', 'description')
        }),
        ("Contact Information", {
            'fields': ('address', 'contact_number', 'email')
        }),
        ("Legal Details", {
            'fields': ('registration_no',)
        }),
    )

    # Taaki admin naya record add na kar sake (Single record policy)
    def has_add_permission(self, request):
        if SchoolSettings.objects.exists():
            return False
        return True

    # Taaki koi setting delete na kar sake (Security)
    def has_delete_permission(self, request, obj=None):
        return False