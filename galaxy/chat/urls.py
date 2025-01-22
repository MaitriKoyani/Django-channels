from django.urls import path

from . import views

urlpatterns = [
    path("chat/", views.index, name="index"),
    path("chat/<str:room_name>/", views.room, name="room"),
    path('login/', views.LoginViews.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]