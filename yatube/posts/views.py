from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Follow, Group, Post, User
from .forms import CommentForm, PostForm
from django.contrib.auth.decorators import login_required


MAX_POSTS = 10


def page_view(post_list, request):
    paginator = Paginator(post_list, MAX_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = (Post.objects.select_related('author', 'group')
                 .order_by('-pub_date'))
    page_obj = page_view(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_list(request):
    template = 'posts/group_list.html'
    return render(request, template)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = (group.group_posts.filter(group=group).
                 select_related('author').order_by('-pub_date'))
    page_obj = page_view(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_count = author.posts.count()
    post_list = author.posts.all()
    page_obj = page_view(post_list, request)
    following = None
    if request.user.is_authenticated:
        following = False
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'author_count': author_count,
        'posts': post_list,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author_count = post.author.posts.count()
    title = post.text[:30]
    form = CommentForm()
    post_comments = post.comments.all()

    context = {
        'post': post,
        'author_count': author_count,
        'title': title,
        'form': form,
        'post_comments': post_comments}
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    TITLE = 'Новый пост'
    if request.method == "POST":
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('yatube_posts:profile', request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    context = {
        'form': form,
        'title': TITLE,
        'is_edit': True}
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('yatube_posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('yatube_posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('yatube_posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followings = request.user.follower.all()
    follow_list = User.objects.filter(following__in=followings)
    post_list = Post.objects.filter(
        author__in=follow_list).select_related(
        'author', 'group')
    page_obj = page_view(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author and not Follow.objects.filter(
            author=author, user=user).exists():
        Follow.objects.create(author=author, user=user)
    return redirect('yatube_posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.get(author=author, user=user).delete()
    return redirect('yatube_posts:profile', username=username)
