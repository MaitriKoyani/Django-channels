from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Member , UserToken
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta
from .decorator import login_required,check_login
from django.utils.decorators import method_decorator
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

# Create your views here.

@login_required
def index(request):
    return render(request, "index.html")

@login_required
def room(request, room_name):
    return render(request, "room.html", {"room_name": room_name,"user_name":request.user.username})

@method_decorator(check_login, name='dispatch')
class RegisterMemberView(APIView):
    def post(self, request):
        data=request.data
        if data:
            member=Member.objects.create(
                username=data['username'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = MemberSerializer(member)
            token = UserToken.objects.create(member=member)
            res = setcookietoken(token)
            res.status_code = status.HTTP_201_CREATED
            res.data = serializer.data
            return res
        return Response({"message":"data not provided",'require':'username,email,password'}, status=status.HTTP_400_BAD_REQUEST)



def setcookietoken(token):
    expires = datetime.utcnow() + timedelta(days=1)
    response = Response()
    response.set_cookie(
        'token',
        token.token,
        expires=expires,
        httponly=True,
        secure=False,#make true when in production
        samesite='Lax',
        path='/'
    )
    return response

class LoginViews(APIView):
    def get(self, request):
        
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        try:

            try:
                user = request.data.get('username')
            except Exception as e:
                print(e)
                return None
            
            user = Member.objects.filter(username= user).first()
            token = UserToken.objects.filter(user=user).first()
            if token:
                res = Response({'message':'Already logged in other browser'},status=status.HTTP_400_BAD_REQUEST)
                return res
            else:
                username = request.data.get('username')
                passwor = request.data.get('password')
                user = Member.objects.filter(username=username).first()
                if user:
                    
                    if passwor == user.password:
                        
                        token = UserToken.objects.create(user=user)
                        res = setcookietoken(token)
                        res.status_code = status.HTTP_200_OK
                        context={'message':'Successfully logged in'}
                        res.data = context
                        return res
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_404_NOT_FOUND)
    
        except Exception as e:
            username = request.data.get('username')
            passwor = request.data.get('password')
            user = Member.objects.filter(username=username).first()
            if user:
                if passwor == user.password:
                    
                    token = UserToken.objects.create(user=user)
                    res = setcookietoken(token)
                    res.status_code = status.HTTP_200_OK
                    context={'message':'Successfully logged in'}
                    res.data = context
                    return res
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_404_NOT_FOUND)

listofemails = []

class forgotpassword(APIView):
    def get(self, request):

        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        email = request.data.get('email')
        member = Member.objects.filter(email=email).first()
        subject = 'Password Reset Request'
        message = 'You have requested to reset your password. Click the link below to set a new password:\n\n' + 'http://127.0.0.1:8000/resetpassword/'
        recipient_email = email
        if member :
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL, 
                    [recipient_email], 
                    fail_silently=False 
                )
                listofemails.append(recipient_email)
                return Response({'success': 'Email sent successfully'})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else :
            return Response({'error': 'User not found of this email'}, status=status.HTTP_404_NOT_FOUND)

class resetpassword(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        newpassword = request.data.get('newpassword')
        confirmpassword = request.data.get('confirmpassword')
        email = listofemails[0]
        if newpassword == confirmpassword:
            print('right')
            member = Member.objects.filter(email=email).first()
            if member:
                member.password = make_password(newpassword)
                member.save()
                listofemails.clear()
                print('set')
                return Response({'success': 'Password reset successfully'},status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
     

@method_decorator(login_required, name='dispatch')
class LogoutView(APIView):
    def get(self, request):
        try:
            print(request.user,'logout')
            res = Response({'message':'Successfully logged out'},status=status.HTTP_200_OK)
            tk = UserToken.objects.filter(user=request.user).all()
            for t in tk:
                t.delete()
            token = request.COOKIES.get('token')
            if token:
                mtoken = UserToken.objects.filter(token=token).first()
                if mtoken:
                    mtoken.delete()

            res.delete_cookie('token')
            return res
        except Exception as e:
            return Response({'error':e},status=status.HTTP_400_BAD_REQUEST)
