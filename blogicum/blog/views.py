from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from blog.models import Post, Category, User, Comment
from blog.utils import get_all_posts, get_relevant_posts
from blog.forms import PostForm, UserForm, CommentForm


PAGE_NUMBER = 10


def index(request):
    template = 'blog/index.html'

    post_list = get_relevant_posts(Post.objects)
    paginator = Paginator(post_list, PAGE_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'

    user = get_object_or_404(User.objects, username=username)

    if request.user == user:
        posts = get_all_posts(Post.objects).filter(author=user)
    else:
        posts = get_relevant_posts(Post.objects).filter(author=user)

    paginator = Paginator(posts, PAGE_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user,
        'page_obj': page_obj,
    }

    return render(request, template, context)


@login_required
def edit_profile(request):
    template = 'blog/user.html'

    username = request.user.get_username()
    print(username)

    instance = get_object_or_404(User, username=username)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=username)

    return render(request, template, context)


@login_required
def create_post(request):
    template = 'blog/create.html'

    form = PostForm(request.POST or None, request.FILES or None)

    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'

    post = get_object_or_404(Post.objects, id=post_id)
    if request.user != post.author:
        post = get_object_or_404(get_relevant_posts(Post.objects), id=post_id)

    form = CommentForm()
    comments = Comment.objects.filter(post=post)

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    template = 'blog/create.html'

    instance = get_object_or_404(Post, pk=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(request.POST or None,
                    request.FILES or None, instance=instance)

    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    template = 'blog/create.html'

    instance = get_object_or_404(Post, pk=post_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:profile', username=request.user.username)

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    template = 'blog/comment.html'

    instance = get_object_or_404(Comment, pk=comment_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    form = CommentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'comment': instance,
    }
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template = 'blog/comment.html'

    instance = get_object_or_404(Comment, pk=comment_id)
    if request.user != instance.author:
        return redirect('blog:post_detail', post_id=post_id)

    context = {
        'comment': instance,
    }
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.filter(is_published=True), slug=category_slug
    )
    post_list = get_relevant_posts(
        category.posts
    )

    paginator = Paginator(post_list, PAGE_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
    }

    return render(request, template, context)
