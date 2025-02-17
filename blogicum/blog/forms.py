from django import forms
from django.contrib.auth.models import User
from .models import Post, Comment


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'image', 'location', 'category')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)