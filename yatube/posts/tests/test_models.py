from django.test import TestCase

from ..models import Group, Post, User


USERNAME = 'leo'
GROUP_SLUG = 'writers'
GROUP_TITLE = 'Тестовая группа'
GROUP_DESCRIPTION = 'Описание тестовой группы'
POST_TEXT = 'Тестовый Текст'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT * 3,
        )

    def test_models_have_correct_objects_names(self):
        field_str = {
            self.post: self.post.text[:15],
            self.group: self.group.title,
        }
        for field, expected_value in field_str.items():
            with self.subTest(field=field):
                self.assertEqual(
                    expected_value, str(field)
                )
