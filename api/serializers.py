from rest_framework import serializers
from .models import Exam, ExamSchedule, StudentMark

class ExamScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSchedule
        fields = ['subject', 'exam_date', 'exam_time', 'total_marks', 'description']

class ExamSerializer(serializers.ModelSerializer):
    # Nested Serializer: Ek exam ke saath uski poori schedule list
    schedule = ExamScheduleSerializer(many=True, source='schedules')

    class Meta:
        model = Exam
        fields = ['id', 'exam_name', 'class_name', 'schedule']

    def create(self, validated_data):
        schedules_data = validated_data.pop('schedules')
        # Pehle Main Exam create karein
        exam = Exam.objects.create(**validated_data)
        # Phir loop chala kar saare subjects save karein
        for schedule_data in schedules_data:
            ExamSchedule.objects.create(exam=exam, **schedule_data)
        return exam
    
class StudentMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMark
        fields = ['student', 'exam', 'subject', 'marks_obtained']