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
from django.contrib import messages

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
        return render(request,'room.html',{"room_name":chatname,"user_name":request.user.username})

@method_decorator(check_login, name='dispatch')
class RegisterView(APIView):
    def post(self, request):
        data=request.data
        print(data)
        if data:
            if Member.objects.filter(username=data['username']).exists():
                messages.error(request, 'Username already exists')
                return redirect('/register/', status=status.HTTP_400_BAD_REQUEST)
            if Member.objects.filter(email=data['email']).exists():
                messages.error(request, 'Email already exists')
                return redirect('/register/', status=status.HTTP_400_BAD_REQUEST)
            print('okay')
            member=Member.objects.create(username=data['username'],email=data['email'],password=make_password(data['password']))
            print('before')
            token = UserToken.objects.create(user=member)
            print('after')
            res = setcookietoken(token)
            
            return res
        messages.error(request, 'data not provided')
        return redirect('/register/',status=status.HTTP_400_BAD_REQUEST)



class LoginViews(APIView):
    def get(self, request):
        
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        if request.data:
            username = request.data.get('username')
            passwor = request.data.get('password')
            user = Member.objects.filter(username=username).first()
            if user:
                istrue = check_password(passwor,user.password)
                if istrue:
                    token = UserToken.objects.filter(user=user).first()
                    if token:
                        token=token
                    else:
                        token = UserToken.objects.create(user=user)
                    res = setcookietoken(token)
                    
                    return res
                messages.error(request, 'Invalid password')
                return redirect('/login/', status=status.HTTP_400_BAD_REQUEST)
            messages.error(request, 'User not found')
            return redirect('/login/',status=status.HTTP_404_NOT_FOUND)
        messages.error(request, 'data not provided')
        return redirect('/login/',status=status.HTTP_400_BAD_REQUEST)

listofemails = []

class ForgotPasswordView(APIView):
    def get(self, request):

        return Response(status=status.HTTP_200_OK)
    def post(self, request):

        if request.data:
            username = request.data.get('username')
            email = request.data.get('email')
            member = Member.objects.filter(username=username,email=email).first()
            if member:
                subject = 'Password Reset Request'
                message = 'You have requested to reset your password. Click the link below to set a new password:\n\n' + 'http://127.0.0.1:8000/resetpassword/'
                recipient_email = email
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL, 
                        [recipient_email], 
                        fail_silently=False 
                    )
                    listofemails.append(recipient_email)
                    messages.success(request, 'Password reset link sent successfully')
                    return redirect('/resetpassword/',status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else :
                messages.error(request, 'User not found enter correct username and email')
                return redirect('/forgotpassword/',status=status.HTTP_404_NOT_FOUND)
        messages.error(request, 'data not provided')
        return redirect('/forgotpassword/',status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        if request.data:
            newpassword = request.data.get('newpassword')
            confirmpassword = request.data.get('confirmpassword')
            email = listofemails[0]
            if newpassword == confirmpassword:
                member = Member.objects.filter(email=email).first()
                if member:
                    member.password = make_password(newpassword)
                    member.save()
                    listofemails.clear()
                    messages.success(request, 'Password reset successfully')
                    return redirect('/login/',status=status.HTTP_200_OK)
                else:
                    messages.error(request, 'User not found')
                    return redirect('/resetpassword/',status=status.HTTP_404_NOT_FOUND)
            messages.error(request, 'Password does not match')
            return redirect('/resetpassword/',status=status.HTTP_400_BAD_REQUEST)
        messages.error(request, 'data not provided')
        return redirect('/resetpassword/',status=status.HTTP_400_BAD_REQUEST)
     

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
                    mtoken.delete()

            res.delete_cookie('token')
            return res
        except Exception as e:
            return Response({'error':e},status=status.HTTP_400_BAD_REQUEST)
        
class AccountView(APIView):
    def get(self, request):
        user = Member.objects.filter(username=request.user.username).first()
        if user:
            profile = Profile.objects.filter(user=user).first()
            print(profile.image,'dfgh')
            serializer = ProfileSerializer(profile)
            print(serializer.data)
            return Response(serializer.data,status=status.HTTP_200_OK)
        messages.error(request, 'User not found')
        return Response(status=status.HTTP_200_OK)

class DelAccountView(APIView):
    def get(self, request):
        try:
            res = redirect('/register/')
            
            token = request.COOKIES.get('token')
            if token:
                mtoken = UserToken.objects.filter(token=token).first()
                if mtoken:
                    mtoken.delete()

            res.delete_cookie('token')
            member = Member.objects.filter(username=request.user.username).first()
            if member:
                for grp_user in member.grpuser_set.all():
                    print(grp_user)
                    if grp_user.group.personal or grp_user.group.grpuser_set.count() == 1:
                        
                        gu = grp_user.group
                        guser = GrpUser.objects.filter(group=gu).all()
                        chat_messages = ChatMessage.objects.filter(grp_user__in=guser).all()
                        for chat_message in chat_messages:
                            chat_message.message_content.delete() 

                        chat_messages.delete()
                        grp_user.group.delete()
                member.delete()
            return res
        except Exception as e:
            return Response({'error':e},status=status.HTTP_400_BAD_REQUEST)

class CreateGroupView(APIView):
    def get(self, request):
        members = Member.objects.exclude(username=request.user.username).all()
        memberserializer = MemberSerializer(members,many=True)
        return Response({"members":memberserializer.data},status=status.HTTP_200_OK)
    def post(self, request):
        if request.data:
            gname = request.data.get('gname')
            members = request.data.getlist('members')
            if members != [] and len(members) >= 2 :
                members.append(request.user.username)
                group = Group.objects.create(name=gname,personal=False)
                for member in members:
                    GrpUser.objects.create(group=group,user=Member.objects.filter(username=member).first())
                    print('created')
                return redirect('/home/')
            else:
                messages.error(request, 'Please! Select minimum 2 members.')
                return redirect('/creategroup/',status=status.HTTP_400_BAD_REQUEST)
        messages.error(request, 'data not provided')
        return redirect('/creategroup/',status=status.HTTP_400_BAD_REQUEST)

class SearchView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        if request.data:
            search = request.data.get('search')
            members = Member.objects.filter(username__icontains=search).all()
            members = members.exclude(username=request.user.username)
            if len(members) != 0:
                    
                return render(request,'memberslist.html',{"members":members},status=status.HTTP_200_OK)
            messages.error(request, 'User not found')
            return redirect('/home/',status=status.HTTP_404_NOT_FOUND)
        messages.error(request, 'data not provided')
        return redirect('/home/',status=status.HTTP_400_BAD_REQUEST)

