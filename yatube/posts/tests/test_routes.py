from django.test import TestCase
from django.urls import reverse

from ..models import Post, User


USERNAME = 'leo'
GROUP_SLUG = 'writers'
POST_TEXT = 'Тестовый Текст'


class RoutesURLTests(TestCase):
    def test_urls_use_correct_routes(self):
        self.user = User.objects.create_user(username=USERNAME)
        self.post = Post.objects.create(
            author=self.user,
            text=POST_TEXT,
        )
        urls = [
            ['/', 'main_page', ''],
            ['/create/', 'post_create', ''],
            [f'/group/{GROUP_SLUG}/', 'groups', [GROUP_SLUG]],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/posts/{self.post.id}/', 'post_detail', [self.post.id]],
            [f'/posts/{self.post.id}/edit/', 'post_edit', [self.post.id]],
            [f'/posts/{self.post.id}/comment/', 'add_comment', [self.post.id]],
            ['/follow/', 'follow_index', ''],
            [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
            [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]]
        ]
        for url, route, arg in urls:
            with self.subTest(url=url):
                self.assertEqual(url, reverse('posts:' + route, args=arg))
