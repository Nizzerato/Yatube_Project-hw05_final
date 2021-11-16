import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, Follow, User
from yatube.settings import POSTS, PROFILE_POSTS


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


HOMEPAGE_URL = reverse('posts:main_page')
CREATE_POST_URL = reverse('posts:post_create')
FOLLOW_INDEX_URL = reverse('posts:follow_index')

USERNAME = 'leo'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
NOT_AUTHOR_USERNAME = 'not_author_username'
GROUP_SLUG = 'writers'
GROUP2_SLUG = 'not-writers'
GROUP_URL = reverse('posts:groups', args=[GROUP_SLUG])
GROUP2_URL = reverse('posts:groups', args=[GROUP2_SLUG])
GROUP_TITLE = 'Тестовая группа'
GROUP2_TITLE = 'Вторая Тестовая Группа'
GROUP_DESCRIPTION = 'Описание тестовой группы'
GROUP2_DESCRIPTION = 'Описание Второй Тестовой Группы'
POST_TEXT = 'Тестовый Текст'
FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_not_author = User.objects.create_user(
            username=NOT_AUTHOR_USERNAME,
        )
        cls.group = Group.objects.create(
            slug=GROUP_SLUG,
            title=GROUP_TITLE,
            description=GROUP_DESCRIPTION,
        )
        cls.group_2 = Group.objects.create(
            title=GROUP2_TITLE,
            slug=GROUP2_SLUG,
            description=GROUP2_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
            group=cls.group,
            image=SimpleUploadedFile(
                name='views_small.gif',
                content=SMALL_GIF,
                content_type='image/gif',
            )
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[
            cls.post.id,
        ])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[
            cls.post.id,
        ])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user_not_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_list_pages_show_correct_context(self):
        Follow.objects.create(
            user=self.user_not_author,
            author=self.user,
        )
        responses = {
            'index': HOMEPAGE_URL,
            'follow_index': FOLLOW_INDEX_URL,
            'group_posts': GROUP_URL,
            'profile': PROFILE_URL,
            'post_detail': self.POST_DETAIL_URL,
        }
        for views_name, url in responses.items():
            with self.subTest(views_name=views_name):
                response = self.another.get(url)
                if 'page_obj' in response.context:
                    page = response.context['page_obj']
                    self.assertEqual(len(page), 1)
                    post_0 = page[0]
                else:
                    post_0 = response.context['post']
                self.assertEqual(post_0, self.post)
                self.assertEqual(post_0.text, self.post.text)
                self.assertEqual(post_0.author, self.post.author)
                self.assertEqual(post_0.group, self.group)
                self.assertEqual(post_0.image, self.post.image)

    def test_group_2_has_zero_posts(self):
        response = self.client.get(GROUP2_URL)
        self.assertNotIn(self.post, response.context.get('page_obj'))

    def test_homepage_cache(self):
        response_1 = self.guest.get(HOMEPAGE_URL)
        Post.objects.all().delete()
        response_2 = self.guest.get(HOMEPAGE_URL)
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.guest.get(HOMEPAGE_URL)
        self.assertNotEqual(response_1.content, response_3.content)

    def test_follow_author(self):
        follow_count = Follow.objects.all().count()
        self.another.get(FOLLOW_URL)
        self.assertEqual(Follow.objects.all().count(), follow_count + 1)
        self.assertTrue(Follow.objects.filter(
            user=self.user_not_author,
            author=self.user,
        ).exists())

    def test_follow_author_second_time(self):
        Follow.objects.create(
            user=self.user_not_author,
            author=self.user,
        )
        follow_count = Follow.objects.all().count()
        self.another.get(FOLLOW_URL)
        self.assertEqual(Follow.objects.all().count(), follow_count)
        self.assertTrue(Follow.objects.filter(
            user=self.user_not_author,
            author=self.user,
        ).exists())

    def test_unfollow_author(self):
        Follow.objects.create(
            user=self.user_not_author,
            author=self.user,
        )
        self.another.get(UNFOLLOW_URL)
        self.assertFalse(Follow.objects.filter(
            user=self.user_not_author,
            author=self.user,
        ).exists())

    def test_self_follow(self):
        self.author.get(FOLLOW_URL)
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user,
        ).exists())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            description=GROUP_DESCRIPTION,
            slug=GROUP_SLUG,
        )

    def test_paginator_shows_correct_records(self):
        posts = [Post(author=self.user,
                      text=f'Тестовый текст {i} поста',
                      group=self.group) for i in range(0, POSTS)]
        Post.objects.bulk_create(posts)
        responses = {
            'posts:main_page': HOMEPAGE_URL,
            'posts:groups': GROUP_URL,
        }
        for views_name, url in responses.items():
            response = self.client.get(url)
            with self.subTest(views_name=views_name):
                self.assertEqual(len(response.context['page_obj']), POSTS)

    def test_paginator_profile_shows_correct_records(self):
        posts = [Post(author=self.user,
                      text=f'Тестовый текст {i} поста',
                      group=self.group) for i in range(0, PROFILE_POSTS)]
        Post.objects.bulk_create(posts)
        response = self.client.get(PROFILE_URL)
        self.assertEqual(len(response.context['page_obj']), PROFILE_POSTS)
