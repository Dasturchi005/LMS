from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .models import Lesson
from .serializers import LessonSerializer

class LessonListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        lessons = Lesson.objects.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'teacher':
            return Response({"detail": "Faqat o'qituvchilar dars yuklay oladi."}, status=403)

        data = {
            "title": request.data.get("title"),
            "description": request.data.get("description"),
            "assignment": request.data.get("assignment"),
            "video": request.FILES.get("video"),
            "image": request.FILES.get("image"),
            "document": request.FILES.get("document"),
        }

        serializer = LessonSerializer(data=data)
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

        serializer = LessonSerializer(lesson, data=request.data)
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