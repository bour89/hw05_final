import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django import forms
from django.conf import settings

from posts.models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
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
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовая пост',
            id='1',
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {reverse('yatube_posts:index'):
                                 'posts/index.html',
                                 reverse('yatube_posts:group_list'):
                                 'posts/group_list.html',
                                 reverse('yatube_posts:profile',
                                         kwargs={'username': 'auth'}):
                                 'posts/profile.html',
                                 reverse('yatube_posts:post_detail',
                                         kwargs={'post_id': 1}):
                                 'posts/post_detail.html',
                                 reverse('yatube_posts:post_create'):
                                 'posts/create_post.html',
                                 reverse('yatube_posts:post_edit',
                                         kwargs={'post_id': 1}):
                                 'posts/create_post.html',
                                 }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('yatube_posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertIsInstance(first_object, Post)
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Тестовая пост')
        self.assertEqual(post_id_0, 1)
        self.assertEqual(post_image_0, 'posts/small3.gif')

    def test_group_posts_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('yatube_posts:group_posts',
                    kwargs={'slug': 'test-slug'}))
        first_object = response.context['page_obj'][0]
        self.assertIsInstance(first_object, Post)
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        post_group_0 = first_object.group.slug
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Тестовая пост')
        self.assertEqual(post_id_0, 1)
        self.assertEqual(post_group_0, 'test-slug')
        self.assertEqual(post_image_0, 'posts/small3.gif')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile_page сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('yatube_posts:profile', kwargs={'username': 'auth'}))
        first_object = response.context['page_obj'][0]
        self.assertIsInstance(first_object, Post)
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_id_0 = first_object.id
        post_group_0 = first_object.group.slug
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Тестовая пост')
        self.assertEqual(post_id_0, 1)
        self.assertEqual(post_group_0, 'test-slug')
        self.assertEqual(post_image_0, 'posts/small3.gif')

    def test_group_posts_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('yatube_posts:post_detail', kwargs={'post_id': '1'}))
        post_object = response.context['post']
        self.assertIsInstance(post_object, Post)
        post_author_0 = post_object.author.username
        post_text_0 = post_object.text
        post_id_0 = post_object.id
        post_group_0 = post_object.group.slug
        post_image_0 = post_object.image
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_text_0, 'Тестовая пост')
        self.assertEqual(post_id_0, 1)
        self.assertEqual(post_group_0, 'test-slug')
        self.assertEqual(post_image_0, 'posts/small3.gif')

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('yatube_posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_home_page_show_correct_context(self):
        """Шаблон для post edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('yatube_posts:post_edit',
                    kwargs={'post_id': 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Проверка кэширование записей на главной странице"""
        response_before = self.authorized_client.get(
            reverse('yatube_posts:index'))
        posts_before = response_before.content
        self.post.delete()
        response_after = self.authorized_client.get(
            reverse('yatube_posts:index'))
        posts_after = response_after.content
        self.assertEqual(posts_before, posts_after)
        cache.clear()
        response_clear = self.authorized_client.get(
            reverse('yatube_posts:index'))
        posts_clear = response_clear.content
        self.assertNotEqual(posts_before, posts_clear)


class FollowViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='user2')
        cls.user3 = User.objects.create_user(username='user3')

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
        )

        cls.post2 = Post.objects.create(
            author=cls.user2,
            group=cls.group,
            text='Тестовая пост2',
            id='2',
        )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user3)

    def test_user_can_follow(self):
        """Проверка что пользователь может подписываться
        на пользователя и удалять подписки"""
        self.authorized_client.get(reverse(
            'yatube_posts:profile_follow',
            kwargs={'username': 'user2'}))
        self.assertTrue(Follow.objects.filter(
            user=self.user, author=self.user2))
        self.authorized_client.get(reverse(
            'yatube_posts:profile_unfollow',
            kwargs={'username': 'user2'}))
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user2))

    def test_follow_post_show_on_follow_page(self):
        """Проверка что пост отображается в ленте у тех,
        кто на него подписан и не отображается у тех,
        кто на него не подписан"""
        self.authorized_client.get(reverse(
            'yatube_posts:profile_follow',
            kwargs={'username': 'user2'}))
        response = self.authorized_client.get(
            reverse('yatube_posts:follow_index'))
        self.assertTrue(len(response.context['page_obj']) > 0)
        response_2 = self.authorized_client2.get(
            reverse('yatube_posts:follow_index'))
        self.assertTrue(len(response_2.context['page_obj']) == 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        for i in range(1, 14):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Тестовая пост {i}',
                id=f'{i}'
            )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('yatube_posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

        response = self.authorized_client.get(reverse(
            'yatube_posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(len(response.context['page_obj']), 10)

        response = self.authorized_client.get(reverse(
            'yatube_posts:group_posts', kwargs={'slug': 'test-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.authorized_client.get(reverse(
            'yatube_posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

        response = self.authorized_client.get(reverse(
            'yatube_posts:profile', kwargs={'username': 'auth'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

        response = self.authorized_client.get(reverse(
            'yatube_posts:group_posts',
            kwargs={'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
