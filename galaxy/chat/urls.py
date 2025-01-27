from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("home/",TemplateView.as_view(template_name="home.html"), name="home"),
    # path("room/",TemplateView.as_view(template_name="room.html"), name="room"),
    path("api/home/",views.HomeView.as_view(), name="home"),
    path("room/", views.RoomView.as_view(), name="room"),
    path("login/",TemplateView.as_view(template_name="login.html"), name="login"),
    path('api/login/', views.LoginViews.as_view(), name='login'),
    path("register/",TemplateView.as_view(template_name="register.html"), name="register"),
    path('api/register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('creategroup/',TemplateView.as_view(template_name="creategroup.html"), name="creategroup"),
    path('account/',TemplateView.as_view(template_name="account.html"), name="account"),
    path('api/account/', views.AccountView.as_view(), name='account'),
    path('deleteaccount/', views.DelAccountView.as_view(), name='account'),
    path('api/creategroup/', views.CreateGroupView.as_view(), name='creategroup'),
    path('forgotpassword/',TemplateView.as_view(template_name="forgotpassword.html"), name="forgotpassword"),
    path('api/forgotpassword/', views.ForgotPasswordView.as_view(), name='forgotpassword'),
    path('resetpassword/',TemplateView.as_view(template_name="resetpassword.html"), name="resetpassword"),
    path('api/resetpassword/', views.ResetPasswordView.as_view(), name='resetpassword'),
    path('api/search/', views.SearchView.as_view(), name='search'),
    path('memberslist/',TemplateView.as_view(template_name="memberslist.html"), name="memberslist"),
    path('api/addrequestfriend/<int:pk>/', views.AddRequestFriendView.as_view(), name='addrequestfriend'),
    path('notifications/',TemplateView.as_view(template_name="notifications.html"), name="notifications"),
    path('api/addfriend/<int:pk>/', views.AddFriendView.as_view(), name='addfriend'),
    path('viewfriends/',TemplateView.as_view(template_name="friends.html"), name="viewfriends"),
    path('api/removefriend/<int:pk>/', views.RemoveFriendView.as_view(), name='removefriend'),
]