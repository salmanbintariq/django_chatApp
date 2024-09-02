from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUSer, name='logout'),
    path('register/', views.registerUser, name='register'),

    path('', views.home, name='home'),
    path('room/<int:id>/', views.room, name='room'),
    path('profile/<int:id>/', views.userProfile, name='user-profile'),

    path('create-room', views.createRoom, name='create-room'),
    path('update-room/<int:id>/', views.roomUpdate, name='update-room'),
    path('delete-room/<int:id>/', views.roomDelet, name='delete-room'),

    path('delete-message/<int:id>/', views.messageDelet, name='delete-message'),

    path('update-user/', views.updateUser, name='update-user'),
    path('topics', views.topicsPage, name='topics'),
    path('activity', views.activityPage, name='activity'),

]
