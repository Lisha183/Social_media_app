from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

# User Model
class User(AbstractUser):
    profile_picture = models.ImageField(upload_to='profles/', null = True, blank = True)
    bio = models.TextField(blank= True)

# Post Model
class Post(models.Model):
    author = models.ForeignKey(User,related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', null = True , blank = True)
    hashtags = models.CharField(max_length=255, blank = True)
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    disliked_by = models.ManyToManyField(User, related_name='disliked_posts', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Post"


# Comments Model
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Likes Model
class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE,  related_name='post_likes',)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

# Follow Model
class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_relationships', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='follower_relationships', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile/', blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='profile_following', blank=True)
    following = models.ManyToManyField('self' ,symmetrical=False, related_name='following_profiles', blank=True)

    def __str__(self):
        return self.user.username

    def followers_count(self):
        return self.followers.count()

    def following_count(self):
        # Use Follow model to count who this user is following
        return Follow.objects.filter(follower=self.user).count()

class PostDislike(models.Model):
    post = models.ForeignKey(Post, related_name='post_dislikes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    class Meta:
        unique_together = ('post', 'user')

