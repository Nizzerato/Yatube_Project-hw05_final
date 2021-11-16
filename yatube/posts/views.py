from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import Group, Post, Follow, User
from .forms import PostForm, CommentForm
from yatube.settings import PROFILE_POSTS, POSTS


def paginate(queryset, request, page_size=POSTS):
    return Paginator(queryset, page_size).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': paginate(Post.objects.all(), request),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': paginate(group.posts.all(), request),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        Follow.objects.filter(user=request.user, author=author).exists()
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': paginate(author.posts.all(), request, PROFILE_POSTS),
        'following': Follow.objects.all(),
    })


def post_detail(request, post_id, form=None):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm(request.POST or None),
        'switched_to_post_detail': True
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {
        'form': form,
    })


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': True,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': paginate(Post.objects.all().filter(
            author__following__user=request.user), request),
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user and not author.following.filter(
        user=request.user,
    ).exists():
        Follow.objects.create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(request.user.follower,
                      author__username=username).delete()
    return redirect('posts:profile', username=username)
