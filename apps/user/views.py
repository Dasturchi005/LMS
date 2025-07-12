from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login

from .models import User
from .serializers import UserSerializer

class UserCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role_to_create = request.data.get('role')
        creator = request.user

        allowed_roles = []
        if creator.is_superuser:
            allowed_roles = ['director', 'admin', 'teacher', 'student', 'parent']
        elif creator.role == 'director':
            allowed_roles = ['admin', 'teacher', 'student', 'parent']
        elif creator.role == 'admin':
            allowed_roles = ['teacher', 'student', 'parent']
        else:
            return Response({"detail": "Siz foydalanuvchi yaratishga ruxsatsiz"}, status=403)

        if role_to_create not in allowed_roles:
            return Response({"detail": f"{creator.role} foydalanuvchi {role_to_create} ni yaratishi mumkin emas."}, status=403)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login muvaffaqiyatli", "role": user.role})
        return Response({"error": "Login yoki parol xato"}, status=401)