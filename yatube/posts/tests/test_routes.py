from django.test import TestCase
from django.urls import reverse


USERNAME = 'leo'
GROUP_SLUG = 'writers'
POST_TEXT = 'Тестовый Текст'
POST_ID = 1


class RoutesURLTests(TestCase):
    def test_urls_use_correct_routes(self):
        urls = [
            ['/', 'main_page', []],
            ['/create/', 'post_create', []],
            [f'/group/{GROUP_SLUG}/', 'groups', [GROUP_SLUG]],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
            [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
            [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
            ['/follow/', 'follow_index', []],
            [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
            [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]]
        ]
        for url, route, arg in urls:
            with self.subTest(url=url):
                self.assertEqual(url, reverse('posts:' + route, args=arg))
