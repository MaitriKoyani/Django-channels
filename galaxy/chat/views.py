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
import os
from django.conf import settings


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
        
        if request.user.is_authenticated :
            user = request.user
            try:
                members = Friends.objects.filter(user=user).first().friend.all()
            except Exception as e:
                print(e)
                return Response({"msg":"members not found"},status=status.HTTP_404_NOT_FOUND)
                
            group = GrpUser.objects.filter(user=user).all()
            gname=[]
            
            for g in group:
                gu = Group.objects.filter(name=g.group.name,personal=False).first()
                if gu:
                    gname.append(gu)
            if members:
                memberserializer = MemberSerializer(members,many=True)
            else:
                return Response({"msg":"members not found"},status=status.HTTP_404_NOT_FOUND)
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
        grp = None
        if isuser:
            temp1 = isuser.username+'_'+request.user.username
            grp1 = Group.objects.filter(name=temp1).first()
            temp2 = request.user.username+'_'+isuser.username
            grp2 = Group.objects.filter(name=temp2).first()
            if grp1:
                chatname = grp1.name
                grp = grp1
            elif grp2:
                chatname = grp2.name
                grp = grp2
            else:
                chatname = temp1
                grp = Group.objects.create(name=chatname,personal=True)
                GrpUser.objects.create(group=grp,user=request.user)
                GrpUser.objects.create(group=grp,user=isuser)
        elif isgrp:
            chatname = isgrp.name
            grp = isgrp
        return render(request,'home.html',{"room_name":chatname,"user_name":request.user.username,"group":grp},status=status.HTTP_200_OK)

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
listofotp = []

class ForgotPasswordView(APIView):
    def get(self, request):

        return Response(status=status.HTTP_200_OK)
    def post(self, request):

        if request.data:
            username = request.data.get('username')
            email = request.data.get('email')
            member = Member.objects.filter(username=username,email=email).first()
            otp=random.randrange(100000,999999,6)
            if member:
                subject = 'Password Reset Request'
                message = 'You have requested to reset your password and HeartTalk send you otp for reset password '+str(otp)+' Please don\'t share with anyone.<br> Thank you!!'
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
                    listofotp.append(otp)
                    print(listofotp)
                    messages.success(request, 'Password reset otp sent successfully')
                    return redirect('/checkotp/',status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else :
                messages.error(request, 'User not found enter correct username and email')
                return redirect('/forgotpassword/',status=status.HTTP_404_NOT_FOUND)
        messages.error(request, 'data not provided')
        return redirect('/forgotpassword/',status=status.HTTP_400_BAD_REQUEST)

class CheckOtpView(APIView):
    def post(self, request):
        if request.data:
            otp = request.data.get('otp')
            if otp == str(listofotp[0]):
                listofotp.clear()
                messages.success(request, 'Otp verified successfully')
                return redirect('/resetpassword/',status=status.HTTP_200_OK)
            messages.error(request, 'Invalid otp')
            return redirect('/checkotp/',status=status.HTTP_400_BAD_REQUEST)
        messages.error(request, 'data not provided')
        return redirect('/checkotp/',status=status.HTTP_400_BAD_REQUEST)

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
            serializer = ProfileSerializer(profile)
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
        members = Friends.objects.filter(user=request.user).first().friend.all()
        print(members)
        # for m in members:
        #     for g in members.exclude(username = m.username):
        #         if m in g.friends.first().friend.all():
                    

            # if members.exclude(username = m.username) in m.friends.first().friend.all():
            #     members = members.exclude(username = m.username)
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

@method_decorator(login_required, name='dispatch')
class SearchView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        if request.data:
            search = request.data.get('search')
            members = Member.objects.filter(username__icontains=search).all()
            members = members.exclude(username=request.user.username)
            frd = Friends.objects.filter(user = request.user).first()
            if len(members) != 0:
                
                return render(request,'addfriend.html',{"members":members},status=status.HTTP_200_OK)
            messages.error(request, 'User not found')
            return redirect('/home/',status=status.HTTP_404_NOT_FOUND)
        messages.error(request, 'data not provided')
        return redirect('/home/',status=status.HTTP_400_BAD_REQUEST)
    
class AddRequestFriendView(APIView):
    def get(self, request,pk):
        sender = Member.objects.filter(username=request.user.username).first()
        member = Member.objects.filter(id=pk).first()
        receiver = Request.objects.filter(receiver=member).first()
        if sender and receiver:
            try:
                receiver.sender.add(sender)
            except Exception as e:
                print(e)
            return redirect('/home/')
        elif sender and not receiver:
            try:
                receiver = Request.objects.create(receiver=member)
                receiver.sender.add(sender)
            except Exception as e:
                print(e)
            return redirect('/home/')
        messages.error(request, 'User not found')
        return redirect('/home/',status=status.HTTP_404_NOT_FOUND)

class AddFriendView(APIView):
    def get(self, request,pk):
        user = Member.objects.filter(username=request.user.username).first()
        print(user)
        if user:
            frd = Friends.objects.filter(user=user).first()
            if frd:
                if Member.objects.filter(id=pk).first() not in frd.friend.all():
                    frd.friend.add(Member.objects.filter(id=pk).first())
                frd = Friends.objects.filter(user=Member.objects.filter(id=pk).first()).first()
                if frd:
                    if user not in frd.friend.all():
                        frd.friend.add(user)
                else:
                    frd = Friends.objects.create(user=Member.objects.filter(id=pk).first())
                    frd.friend.add(user)
            else:
                frd = Friends.objects.create(user=user)
                frd.friend.add(Member.objects.filter(id=pk).first())

                frd = Friends.objects.filter(user=Member.objects.filter(id=pk).first()).first()
                if frd:
                    if user not in frd.friend.all():
                        frd.friend.add(user)
                else:
                    frd = Friends.objects.create(user=Member.objects.filter(id=pk).first())
                    frd.friend.add(user)
            receiver = Request.objects.filter(receiver=user).first()
            if receiver:
                try:
                    receiver.sender.remove(Member.objects.filter(id=pk).first())
                    if receiver.sender.count() == 0:
                        receiver.delete()
                except Exception as e:
                    print(e)
            return redirect('/notifications/')
        messages.error(request, 'User not found')
        return redirect('/home/',status=status.HTTP_404_NOT_FOUND)
    
class RemoveFriendView(APIView):
    def get(self, request,pk):
        user = Member.objects.filter(username=request.user.username).first()
        if user:
            frd = Friends.objects.filter(user=user).first()
            if frd:
                try:
                    frd.friend.remove(Member.objects.filter(id=pk).first())
                    if frd.friend.count() == 0:
                        frd.delete()
                except Exception as e:
                    print(e)
            return redirect('/viewfriends/')
        messages.error(request, 'User not found')
        return redirect('/home/',status=status.HTTP_404_NOT_FOUND)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','webp'}

def allowed_file(filename):
    print('file allow')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    return str(uuid.uuid4()) + '_' + filename

def upload_file(file,uname):
        
        UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media\\profile_pics\\',uname)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        
        if file and allowed_file(file.name):
            
            filename = get_unique_filename(file.name)
            
            path = "R:\\programs\\channels\\galaxy\\media\\profile_pics\\"+uname
            
            path=os.path.join(path, filename)

            with open(path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            
            return filename
        else:
            print('file not allow')

class ChangeProfileView(APIView):
    def post(self, request):
        if request.data:
            print('hi')
            user = Member.objects.filter(username=request.user.username).first()
            if user:
                print('hello')
                profile = Profile.objects.filter(user=user).first()
                if profile:
                    profile.up_id = request.data.get('up_id')
                
                    print('yey')
                    print(request.data)
                    print(request.data.get('files'))
                    print(request.FILES.get('files'))
                    if request.FILES:
                        print('files')
                        file = request.FILES['files']
                        
                        filename = upload_file(file,user.username)
                        print(filename)
                        filename = 'profile_pics/'+user.username+'/'+filename
                        profile.image = filename
                    else:
                        print('url')
                        profile.image = request.data.get('url')
                    print('bio')
                    profile.bio = request.data.get('bio')
                    profile.save()
                    return redirect('/account/')
            messages.error(request, 'User not found')
            return redirect('/changeprofile/',status=status.HTTP_404_NOT_FOUND)
        messages.error(request, 'data not provided')
        return redirect('/changeprofile/',status=status.HTTP_400_BAD_REQUEST)