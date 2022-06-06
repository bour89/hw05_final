from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.forbidden_error'
handler500 = 'core.views.internal_server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('posts.urls', namespace='yatube_posts')),
    path('group_list.html', include('posts.urls', namespace='yatube_posts')),
    path('about/', include('about.urls', namespace='about')),
    path('group/<slug:slug>/', include('posts.urls',
         namespace='yatube_posts')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('profile/<str:username>/', include('posts.urls',
         namespace='yatube_posts')),
    path('posts/<int:post_id>/', include('posts.urls',
         namespace='yatube_posts')),
    path('create/', include('posts.urls',
         namespace='yatube_posts')),
    path('posts/<int:post_id>/edit/', include('posts.urls',
         namespace='yatube_posts')),
    path('posts/<int:post_id>/comment/', include('posts.urls',
         namespace='yatube_posts')),
    path('follow/', include('posts.urls', namespace='yatube_posts')),
    path('profile/<str:username>/follow/', include('posts.urls',
         namespace='yatube_posts')),
    path('profile/<str:username>/unfollow/', include('posts.urls',
         namespace='yatube_posts')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
