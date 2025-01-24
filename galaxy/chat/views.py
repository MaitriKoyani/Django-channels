from django.shortcuts import render,redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Member , UserToken
from django.contrib.auth.hashers import make_password,check_password
from datetime import datetime, timedelta
from .decorator import login_required,check_login
from django.utils.decorators import method_decorator
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime

# Create your views here.

def setcookietoken(token):
    expires = datetime.utcnow() + timedelta(days=1)
    response = redirect('/home/')
    response.set_cookie(
        'token',
        token.token,
        expires=expires,
        httponly=False,#make true when in production
        secure=False,#make true when in production
        samesite='Lax',
        path='/'
    )
    return response

@method_decorator(login_required, name='dispatch')
class HomeView(APIView):
    def get(self, request):
        print(request,request.user)
        if request.user.is_authenticated :
            user = request.user
            members = Member.objects.exclude(username=user.username).all()
            group = GrpUser.objects.filter(user=user).all()
            gname=[]
            for g in group:
                gu = Group.objects.filter(name=g.group.name,personal=False).first()
                if gu:
                    gname.append(gu)
            memberserializer = MemberSerializer(members,many=True)
            grpuserserializer = GroupSerializer(gname,many=True)
            return Response({"members":memberserializer.data,"groups":grpuserserializer.data},status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(login_required, name='dispatch')
class RoomView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        chatname = request.data.get('chat_name')
        isuser = Member.objects.filter(username=chatname).first()
        isgrp = Group.objects.filter(name=chatname).first()
        if isuser:
            temp1 = isuser.username+'_'+request.user.username
            grp1 = Group.objects.filter(name=temp1).first()
            temp2 = request.user.username+'_'+isuser.username
            grp2 = Group.objects.filter(name=temp2).first()
            if grp1:
                chatname = grp1.name
            elif grp2:
                chatname = grp2.name
            else:
                chatname = temp1
                grp = Group.objects.create(name=chatname,personal=True)
                GrpUser.objects.create(group=grp,user=request.user)
                GrpUser.objects.create(group=grp,user=isuser)
        elif isgrp:
            chatname = isgrp.name
        print(chatname)
        # return Response({"chat_name":chatname},status=status.HTTP_200_OK)
        return render(request,'room.html',{"room_name":chatname,"user_name":request.user.username})

@method_decorator(check_login, name='dispatch')
class RegisterView(APIView):
    def post(self, request):
        data=request.data
        print('data')
        if data:
            print('yes')
            if Member.objects.filter(username=data['username']).exists():
                return Response({"message":"Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if Member.objects.filter(email=data['email']).exists():
                return Response({"message":"Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            member=Member.objects.create(username=data['username'],email=data['email'],password=make_password(data['password']))
            print('hi user before')
            print(member)
            token = UserToken.objects.create(user=member)
            print('hi user after')
            res = setcookietoken(token)
            
            return res
        return Response({"message":"data not provided",'require':'username,email,password'}, status=status.HTTP_400_BAD_REQUEST)



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
            print('dfghj')
            if token:
                res = Response({'message':'Already logged in other browser'},status=status.HTTP_400_BAD_REQUEST)

                return res
            else:
                print('deeppp')
                username = request.data.get('username')
                passwor = request.data.get('password')
                user = Member.objects.filter(username=username).first()
                if user:
                    istrue = check_password(passwor,user.password)
                    if istrue:
                        
                        token = UserToken.objects.create(user=user)
                        res = setcookietoken(token)
            
                        return res
                    return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
        except Exception as e:
            username = request.data.get('username')
            passwor = request.data.get('password')
            user = Member.objects.filter(username=username).first()
            if user:
                istrue = check_password(passwor,user.password)
                if istrue:
                    
                    token = UserToken.objects.create(user=user)
                    res = setcookietoken(token)
                    
                    return res
                return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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
            res = redirect('/login/')
            
            token = request.COOKIES.get('token')
            if token:
                mtoken = UserToken.objects.filter(token=token).first()
                if mtoken:
                    print('delete')
                    mtoken.delete()

            res.delete_cookie('token')
            return res
        except Exception as e:
            return Response({'error':e},status=status.HTTP_400_BAD_REQUEST)
        
