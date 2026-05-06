from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User, VerificationStatus
from .serializers import UserSerializer, DocumentUploadSerializer


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        phone = request.data.get('phone')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not email or not phone or not password:
            return Response({
                'error': 'email, phone и password обязательны'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'пользователь с таким email уже существует'},
                          status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone=phone).exists():
            return Response({'error': 'пользователь с таким телефоном уже существует'},
                          status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=email,
            phone=phone,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            })

        return Response({'error': 'неверный email или пароль'},
                       status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadDocumentsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        data = serializer.validated_data

        user.passport_series = data.get('passport_series', user.passport_series)
        user.passport_number = data.get('passport_number', user.passport_number)
        user.passport_issued_by = data.get('passport_issued_by', user.passport_issued_by)
        user.passport_expiry_date = data.get('passport_expiry_date', user.passport_expiry_date)
        user.driving_license_number = data.get('driving_license_number', user.driving_license_number)
        user.driving_license_category = data.get('driving_license_category', user.driving_license_category)
        user.driving_license_expiry_date = data.get('driving_license_expiry_date', user.driving_license_expiry_date)
        user.verification_status = VerificationStatus.PENDING
        user.save()

        return Response({
            'message': 'документы загружены, ожидайте верификации',
            'status': user.verification_status
        })

class VerifyUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.role != 'admin':
            return Response({'error': 'доступ только для администраторов'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
            user.is_verified = True
            user.verification_status = VerificationStatus.VERIFIED
            user.save()
            return Response({'message': f'пользователь {user.email} верифицирован'})
        except User.DoesNotExist:
            return Response({'error': 'пользователь не найден'},
                            status=status.HTTP_404_NOT_FOUND)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'admin':
            return Response({'error': 'доступ только для администраторов'},
                            status=status.HTTP_403_FORBIDDEN)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)