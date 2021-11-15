import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


HOMEPAGE_URL = reverse('posts:main_page')
CREATE_POST_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')
FOLLOW_INDEX_URL = reverse('posts:follow_index')

UNEXPECTED_URL = '/unexpected_url/'

USERNAME = 'leo'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
NOT_AUTHOR_USERNAME = 'not_author_username'
GROUP_SLUG = 'writers'
GROUP_URL = reverse('posts:groups', args=[GROUP_SLUG])
GROUP_TITLE = 'Тестовая группа'
GROUP_DESCRIPTION = 'Описание тестовой группы'
POST_TEXT = 'Тестовый Текст'
FOLLOW_URL = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USERNAME])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_not_author = User.objects.create_user(
            username=NOT_AUTHOR_USERNAME
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[
            cls.post.id,
        ])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[
            cls.post.id,
        ])
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.user_not_author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_urls_exist_at_desired_location(self):
        client_urls = [
            [HOMEPAGE_URL, self.guest_client, 200],
            [PROFILE_URL, self.guest_client, 200],
            [GROUP_URL, self.guest_client, 200],
            [self.POST_DETAIL_URL, self.guest_client, 200],
            [CREATE_POST_URL, self.authorized_client, 200],
            [self.POST_EDIT_URL, self.authorized_client, 200],
            [CREATE_POST_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.not_author_client, 302],
            [UNEXPECTED_URL, self.guest_client, 404],
            [FOLLOW_INDEX_URL, self.authorized_client, 200],
            [FOLLOW_INDEX_URL, self.not_author_client, 200],
            [FOLLOW_INDEX_URL, self.guest_client, 302],
            [FOLLOW_URL, self.not_author_client, 302],
            [FOLLOW_URL, self.guest_client, 302],
            [UNFOLLOW_URL, self.not_author_client, 302],
            [UNFOLLOW_URL, self.guest_client, 302]
        ]
        for url, client, code in client_urls:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_urls_redirects_anonym(self):
        client_urls = [
            [CREATE_POST_URL, self.guest_client,
                f'{LOGIN_URL}?next={CREATE_POST_URL}'],
            [self.POST_EDIT_URL, self.guest_client,
                f'{LOGIN_URL}?next={self.POST_EDIT_URL}'],
            [self.POST_EDIT_URL, self.not_author_client, self.POST_DETAIL_URL],
            [FOLLOW_URL, self.guest_client,
                f'{LOGIN_URL}?next={FOLLOW_URL}'],
            [UNFOLLOW_URL, self.guest_client,
                f'{LOGIN_URL}?next={UNFOLLOW_URL}'],
            [FOLLOW_INDEX_URL, self.guest_client,
                f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'],
        ]
        for url, client, redirect in client_urls:
            with self.subTest(url=url):
                response = client.get(url, follow=False)
                self.assertRedirects(response, redirect)

    def test_urls_use_correct_templates(self):
        template_url_names = [
            [HOMEPAGE_URL, self.guest_client, 'posts/index.html'],
            [GROUP_URL, self.guest_client, 'posts/group_list.html'],
            [PROFILE_URL, self.guest_client, 'posts/profile.html'],
            [self.POST_DETAIL_URL,
                self.guest_client,
                'posts/post_detail.html'],
            [CREATE_POST_URL,
                self.authorized_client,
                'posts/create_post.html'],
            [self.POST_EDIT_URL,
                self.authorized_client,
                'posts/create_post.html'],
            [FOLLOW_INDEX_URL,
                self.authorized_client,
                'posts/follow.html'],
        ]
        for url, client, template in template_url_names:
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    client.get(url), template
                )
