from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from rest_framework_jwt.settings import api_settings
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from .serializers import TokenSerializer, RegisterSerializer, LoginSerializer


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

User = get_user_model()


class ApiLoginView(generics.CreateAPIView):
    """
    POST auth/login/
    """
    permission_classes = (permissions.AllowAny, )
    queryset = User.objects.all()
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        print(self.serializer_class.data)
        username = 'admin'
        password = 'adminadm'
        print('works!nmm', username, password)
        user = authenticate(request, username=username, password=password)
        print('user', user)
        if user is not None:
            login(request, user)
            token = jwt_encode_handler(jwt_payload_handler(user))
            # serializer.is_valid()
            return Response({
                'token': token
            })
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class RegisterUsers(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny, )
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        email = request.data.get("email", "")
        if not username or not password or not email:
            return Response(
                data={
                    'message': "Credentials int valid!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        qs_exists = User.objects.filter(username=username)
        if qs_exists:
            return Response(
                data={
                    'message': 'The user already exists'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        new_user = User.objects.create(
            username=username,
            password=password,
            email=email
        )

        return Response(status=status.HTTP_201_CREATED)