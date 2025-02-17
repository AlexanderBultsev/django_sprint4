from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from .forms import ProfileForm, PostForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DetailView, CreateView, DeleteView, ListView


POST_NUMBER = 10


def filter_posts(posts):
    return posts.filter(
        Q(pub_date__lte=now())
        & Q(is_published=True)
        & Q(category__is_published=True)
    )


def login_redirect(request):
    return redirect(reverse_lazy('blog:profile', kwargs={'username': request.user.username}))




class ProfileDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = POST_NUMBER

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = Post.objects.select_related('category', 'author', 'location').filter(author=self.object)

        if self.request.user.username != self.kwargs['username']:
            posts = filter_posts(posts)
        
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)

        context['user'] = self.request.user
        return context
    
    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})




class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    
    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author != self.request.user:
            raise PermissionDenied
        return post
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})
    

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if post.author != self.request.user:
            raise PermissionDenied
        return post

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})




class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    post_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if comment.author != self.request.user:
            raise PermissionDenied
        return comment
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        if comment.author != self.request.user:
            raise PermissionDenied
        return comment
    
    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})




class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POST_NUMBER

    def get_queryset(self):
        queryset = super().get_queryset()
        return filter_posts(queryset)


class CategoryView(DetailView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = POST_NUMBER

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        posts = filter_posts(self.object.posts.select_related('category', 'author', 'location'))

        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)

        return context
    
    def get_object(self):
        return get_object_or_404(Category.objects.filter(is_published=True), slug=self.kwargs['category_slug'])
