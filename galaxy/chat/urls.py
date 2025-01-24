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
    path('deleteaccount/', views.DelAccountView.as_view(), name='account'),
    # path('api/creategroup/', views.CreateGroupView.as_view(), name='creategroup'),
]