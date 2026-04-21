from rest_framework import generics
from user_auth_app.models import UserProfile
from .serializers import UserProfileSerializer, SimpleUserSerializer
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from .serializers import RegistrationSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from django.contrib.auth.models import User


class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get(self, request):
        return super().get(request)


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all().values('id', 'email', 'username')
        return Response(list(users))


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer


class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'fullname': user.first_name,
                'email': user.email,
                'user_id': user.id
            }, status=201)

        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=email, password=password)

        if not user:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "fullname": user.first_name,
            "email": user.email,
            "user_id": user.id
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = getattr(request.user, 'auth_token', None)

        if token:
            token.delete()

        return Response({"detail": "Logout erfolgreich. Token wurde gelöscht."}, status=status.HTTP_200_OK)


class CheckEmailPermission(BasePermission):
    message = "Nicht autorisiert. Der Benutzer muss eingeloggt sein."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class EmailCheckView(APIView):
    permission_classes = [CheckEmailPermission]

    def get(self, request):
        email = request.query_params.get('email', None)

        if not email:
            return Response(status=400)

        try:
            user = User.objects.get(email=email)
            serializer = SimpleUserSerializer(user)
            return Response(serializer.data, status=200)
        except User.DoesNotExist:
            return Response(status=404)
        except Exception:
            return Response(status=500)
