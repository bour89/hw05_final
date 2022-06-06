import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Comment, Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='small3.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовая пост',
            id='1',
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем гостевой клиент
        self.guest_client = Client()

    def test_create_post(self):
        """Проверка формы создания поста"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': self.group.pk,
            'image': 'image'
        }

        response = self.authorized_client.post(
            reverse('yatube_posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'yatube_posts:profile', kwargs={'username': PostFormTests.user}))
        self.assertEqual(Post.objects.count(), (posts_count + 1))
        self.assertEqual(Post.objects.get(id=1).image, 'posts/small3.gif')
        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group,
                author=PostFormTests.user,
                text='Тестовая пост',
                image='posts/small3.gif',
            ).exists())

    def test_edit_post(self):
        """Проверка формы редактировная поста"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': self.group.pk,
        }

        self.authorized_client.post(
            reverse('yatube_posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                group=PostFormTests.group,
                author=PostFormTests.user,
                text='text',
                id='1'
            ).exists())

        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_cant_create_post(self):
        """Проверка что гостевой клиент не имеет прав
           создавать запись"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': self.group.pk,
        }

        self.guest_client.post(
            reverse('yatube_posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )

        self.assertFalse(
            Post.objects.filter(
                group=PostFormTests.group,
                author=PostFormTests.user,
                text='text',
                id='1'
            ).exists())

        self.assertEqual(Post.objects.count(), posts_count)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
            id='1',)
        cls.text = 'Тестовый коммент'

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем гостевой клиент
        self.guest_client = Client()

    def test_create_comment(self):
        """Проверка формы создания комментария и
        вывода его на страницу поста"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': self.text,
        }

        self.authorized_client.post(
            reverse('yatube_posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), (comment_count + 1))
        self.assertTrue(
            Comment.objects.filter(
                author=CommentFormTests.user,
                text='Тестовый коммент',
            ).exists())

        response = self.authorized_client.get(reverse(
            'yatube_posts:post_detail',
            kwargs={'post_id': self.post.id}))
        self.assertTrue(len(response.context['post_comments']) > 0)

    def test_guest_cant_comment(self):
        """Проверка что гостевой клиент не имеет прав
           создавать коммент"""
        comment_count = Comment.objects.count()
        form_data = {
            'text': self.text,
        }

        self.guest_client.post(
            reverse('yatube_posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
        self.assertFalse(
            Comment.objects.filter(
                author=CommentFormTests.user,
                text='Тестовый коммент',
            ).exists())
