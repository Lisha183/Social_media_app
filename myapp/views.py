from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.views import View
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import *
from .serializers import PostSerializer, RegisterSerializer
from .forms import  *
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

#  Home View 
class HomeView(APIView):
  def get(self, request):
    return render(request, 'home.html')

class SignUpView(CreateView):
    template_name = 'signup.html'
    form_class = SignUpForm  
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'],
        )
        if user is not None:
            login(self.request, user)
        return response
    

# View/Create Posts

class PostView(LoginRequiredMixin, View):
    def get(self, request):
        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'posts.html', {'posts': posts})

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('posts')
        posts = Post.objects.all().order_by('-created_at')
        return render(request, 'posts.html', {'posts': posts, 'form': form})


# View/Update Profile 
class ProfileView(LoginRequiredMixin, View):
    def get(self, request, user_id):
        user_obj = get_object_or_404(User, id=user_id)
        profile = get_object_or_404(Profile, user=user_obj)
        form = ProfileForm(instance=profile)

        posts = Post.objects.filter(author=user_obj).order_by('-created_at')  # fixed here
        followers = Follow.objects.filter(following=user_obj)
        following = Follow.objects.filter(follower=user_obj)

        is_own_profile = request.user.id == user_id
        is_following = followers.filter(follower=request.user).exists()

        context = {
            'profile': profile,
            'form': form,
            'posts': posts,
            'followers': followers,
            'following': following,
            'is_own_profile': is_own_profile,
            'is_following': is_following,
            'user_obj': user_obj,
        }
        return render(request, 'profile.html', context)

    def post(self, request, user_id):
        if request.user.id != user_id:
            return render(request, 'unauthorized.html')

        profile = get_object_or_404(Profile, user__id=user_id)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user_id)

        posts = Post.objects.filter(author=profile.user).order_by('-created_at')  # fixed here
        followers = Follow.objects.filter(following=profile.user)
        following = Follow.objects.filter(follower=profile.user)

        return render(request, 'profile.html', {
            'profile': profile,
            'form': form,
            'posts': posts,
            'followers': followers,
            'following': following,
            'is_own_profile': True,
        })

#Like Post
class LikePostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        post.likes.add(request.user)
        return redirect('feed')


# Comment on Post 
class CommentPostView(LoginRequiredMixin, View):
    def post(self, request, post_id):
        content = request.POST.get('content')
        if content:
            post = Post.objects.get(id=post_id)
            Comment.objects.create(post=post, user=request.user, content=content)
        return redirect('feed')

# Follow User 
class FollowUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        to_follow = User.objects.get(id=user_id)
        if request.user != to_follow:
            Follow.objects.get_or_create(follower=request.user, following=to_follow)
        return redirect('profile', user_id=user_id)

class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm

@login_required
def feed(request):
    posts = Post.objects.all().prefetch_related('post_dislikes', 'post_likes')  # prefetch related likes/dislikes
    following_users = request.user.profile.following.values_list('id', flat=True)
    disliked_post_ids = PostDislike.objects.filter(user=request.user).values_list('post_id', flat=True) if request.user.is_authenticated else []
    liked_post_ids = Like.objects.filter(user=request.user, post__in=posts).values_list('post_id', flat=True)

    return render(request, 'feed.html', {
        'posts': posts,
        'disliked_post_ids': disliked_post_ids,
        'liked_post_ids': liked_post_ids,
        'following_users': following_users,
        })

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, author=request.user, content=content)
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Remove any existing dislike first
    PostDislike.objects.filter(post=post, user=request.user).delete()

    # Toggle like: if exists, remove it; if not, create it
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        # Like exists, so remove it (toggle off)
        like.delete()

    return redirect(request.META.get('HTTP_REFERER', 'feed'))


@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Remove any existing like first
    Like.objects.filter(post=post, user=request.user).delete()

    # Toggle dislike: if exists, remove it; if not, create it
    dislike, created = PostDislike.objects.get_or_create(post=post, user=request.user)
    if not created:
        # Dislike exists, so remove it (toggle off)
        dislike.delete()

    return redirect(request.META.get('HTTP_REFERER', 'feed'))

def search_users(request):
    query = request.GET.get('q')
    users = User.objects.filter(username__icontains=query)
    return render(request, 'search_results.html', {'users': users, 'query': query})

@login_required
def follow_user(request, user_id):
    to_follow = get_object_or_404(User, id=user_id)
    if request.user != to_follow:
        Follow.objects.get_or_create(follower=request.user, following=to_follow)
    return redirect('profile', user_id=user_id)

@login_required
def unfollow_user(request, user_id):
    to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=to_unfollow).delete()
    return redirect('profile', user_id=user_id)

@login_required
def like_post(request, post_id):
    photo = get_object_or_404(Post, pk=post_id)
    if request.user in photo.disliked_by.all():
        photo.disliked_by.remove(request.user)
    photo.liked_by.add(request.user)
    return redirect('feed')  # Assuming 'feed' is the name of your post list view

@login_required
def dislike_post(request, post_id):
    photo = get_object_or_404(Post, pk=post_id)
    if request.user in photo.liked_by.all():
        photo.liked_by.remove(request.user)
    photo.disliked_by.add(request.user)
    return redirect('feed')


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('profile', user_id=user_id)


@login_required
def followers_list_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    followers = profile.followers.all()  # Assuming this is a related manager for followers

    return render(request, 'followers_list.html', {
        'profile_user': user,
        'followers': followers,
    })


def following_list_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    following_relationships = Follow.objects.filter(follower=profile_user)
    following_users = [f.following for f in following_relationships]

    return render(request, 'following_list.html', {
        'profile_user': profile_user,
        'following': following_users
    })

def user_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'profile.html', {'user': user})