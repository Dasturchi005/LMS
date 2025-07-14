from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from .models import Lesson, LessonSubmission
from .serializers import LessonSerializer, LessonSubmissionSerializer

class LessonListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lessons = Lesson.objects.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Faqat teacher yuklay oladi
        if request.user.role != 'teacher':
            return Response({"detail": "Faqat o'qituvchilar dars yuklay oladi."}, status=403)

        serializer = LessonSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class LessonDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        serializer = LessonSerializer(lesson)
        return Response(serializer.data)

    def put(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)

        if request.user.role != 'teacher' or request.user != lesson.created_by:
            return Response({"detail": "Faqat o'z darsingizni o'zgartira olasiz"}, status=403)

        serializer = LessonSerializer(lesson, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)

        if request.user.is_superuser:
            lesson.delete()
            return Response({"message": "Superuser tomonidan o'chirildi"}, status=204)

        if request.user.role == 'teacher' and request.user == lesson.created_by:
            lesson.delete()
            return Response({"message": "Teacher o'z darsini o'chirdi"}, status=204)

        return Response({"detail": "Siz bu darsni o'chira olmaysiz"}, status=403)


class LessonSubmissionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        # Faqat student topshiriq yubora oladi
        if request.user.role != 'student':
            return Response({"detail": "Faqat talabalar topshiriq yubora oladi."}, status=403)

        lesson = get_object_or_404(Lesson, pk=lesson_id)

        # Avval yuborganmi tekshiramiz
        if LessonSubmission.objects.filter(lesson=lesson, student=request.user).exists():
            return Response({"detail": "Siz bu darsga allaqachon fayl yuborgansiz."}, status=400)

        # Fayllar sonini cheklaymiz
        uploaded_files = request.FILES.getlist('files')
        if len(uploaded_files) > 5:
            return Response({"detail": "Bir martada 5 tagacha fayl yuborish mumkin."}, status=400)

        # Saqlash
        for f in uploaded_files:
            LessonSubmission.objects.create(
                lesson=lesson,
                student=request.user,
                file=f
            )

        return Response({"message": "Fayllar muvaffaqiyatli yuborildi."}, status=201)

    def get(self, request, lesson_id):
        submissions = LessonSubmission.objects.filter(lesson_id=lesson_id, student=request.user)
        serializer = LessonSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)