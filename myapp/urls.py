from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from .views import *

urlpatterns = [
    path('', views.feed, name='feed'),
    path('feed/', views.feed, name='feed'),
    path('signup/', SignUpView.as_view(), name = 'signup'),
    path('login/', CustomLoginView.as_view(), name = 'login'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('posts/', PostView.as_view(), name='posts'),
    path('profile/<int:user_id>/', ProfileView.as_view(), name='profile'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('followers/<str:username>/', views.followers_list_view, name='followers_list'),
    path('following/<str:username>/', views.following_list_view, name='following_list'),
    path('u/<str:username>/', views.user_profile_view, name='user_profile'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('search/', views.user_search, name='user_search'),

]
