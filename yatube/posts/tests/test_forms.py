import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


from ..forms import PostForm
from ..models import Group, Post, Comment, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


HOMEPAGE_URL = reverse('posts:main_page')
CREATE_POST_URL = reverse('posts:post_create')
LOGIN_URL = reverse('users:login')

USERNAME = 'leo'
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
NOT_AUTHOR_USERNAME = 'not_author_username'
GROUP_SLUG = 'writers'
GROUP2_SLUG = 'not-writers'
GROUP_TITLE = 'Тестовая Группа'
GROUP2_TITLE = 'Вторая Тестовая Группа'
GROUP_DESCRIPTION = 'Описание Тестовой Группы'
GROUP2_DESCRIPTION = 'Описание Второй Тестовой Группы'
POST_TEXT = 'Тестовый Текст'
COMMENT_TEXT = 'Тестовый Текст Комментария'

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_not_author = User.objects.create_user(
            username=NOT_AUTHOR_USERNAME,
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            description=GROUP_DESCRIPTION,
            slug=GROUP_SLUG,
        )
        cls.group_2 = Group.objects.create(
            title=GROUP2_TITLE,
            slug=GROUP2_SLUG,
            description=GROUP2_DESCRIPTION,
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
        cls.ADD_COMMENT_URL = reverse('posts:add_comment', args=[
            cls.post.id,
        ])
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.user_not_author)
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_create_post(self):
        Post.objects.all().delete()
        image = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif',
        )
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': image,
        }
        response = self.author.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        page_obj = response.context['page_obj']
        post = page_obj[0]
        self.assertEqual(len(page_obj), 1)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group_id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, f"posts/{form_data['image']}")

    def test_post_edit(self):
        image2 = SimpleUploadedFile(
            name='small2.gif',
            content=SMALL_GIF,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Второй Тестовый Текст',
            'group': self.group_2.id,
            'image': image2,
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group_id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, f"posts/{form_data['image']}")

    def test_create_or_edit_post_pages_show_correct_context(self):
        responses = {
            'post_create': CREATE_POST_URL,
            'post_edit': self.POST_EDIT_URL,
        }
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for views_name, url in responses.items():
            for value, expected in form_fields.items():
                response = self.author.get(url)
                with self.subTest(views_name=views_name):
                    form_field = response.context['form'].fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_user_create_comment(self):
        Comment.objects.all().delete()
        form_data = {
            'text': COMMENT_TEXT,
        }
        response = self.author.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        comment = Comment.objects.all()[0]
        self.assertEqual(Comment.objects.all().count(), 1)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.author, self.user)

    def test_anonym_create_comment(self):
        Comment.objects.all().delete()
        comment_form_data = {
            'text': 'anonym text'
        }
        comment_response = self.guest.post(
            self.ADD_COMMENT_URL,
            data=comment_form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.all().count(), 0)
        self.assertRedirects(comment_response,
                             f'{LOGIN_URL}?next={self.ADD_COMMENT_URL}')

    def test_anonym_create_post(self):
        Post.objects.all().delete()
        image = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif',
        )
        post_form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': image,
        }
        post_response = self.guest.post(
            CREATE_POST_URL,
            data=post_form_data,
            follow=True
        )
        self.assertEqual(Post.objects.all().count(), 0)
        self.assertRedirects(post_response,
                             f'{LOGIN_URL}?next={CREATE_POST_URL}')

    def test_anonym_or_not_author_edit_post(self):
        Post.objects.all().delete()
        Group.objects.all().delete()
        self.group = Group.objects.create(
            title=GROUP_TITLE,
            description=GROUP_DESCRIPTION,
            slug=GROUP_SLUG,
        )
        self.post = Post.objects.create(
            author=self.user,
            text=POST_TEXT,
            group=self.group,
        )
        form_data = {
            'text': 'Тестовый Текст Анонима',
            'group': self.group_2.id,
        }
        edit_responses = [
            [self.POST_EDIT_URL, self.guest,
                f'{LOGIN_URL}?next={self.POST_EDIT_URL}'],
            [self.POST_EDIT_URL, self.another,
                f'{LOGIN_URL}?next={self.POST_EDIT_URL}'],
        ]
        for url, client, redirect in edit_responses:
            with self.subTest(url=url, client=client):
                response = self.client.post(url, data=form_data, follow=True)
                post = Post.objects.all()[0]
                self.assertRedirects(response, redirect)
                self.assertEqual(post.text, POST_TEXT)
                self.assertEqual(post.author, self.user)
                self.assertEqual(post.group, self.group)
