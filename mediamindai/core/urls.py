from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.home, name='home'),
    path('chat/new/', views.new_chat, name='new_chat'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),

    path('chat/<int:chat_id>/delete/', views.delete_chat, name='delete_chat'),
    path('chat/<int:chat_id>/rename/', views.rename_chat, name='rename_chat'),
    path("chat/<int:chat_id>/api/", views.chat_api_reply, name="chat_api_reply"),
]

