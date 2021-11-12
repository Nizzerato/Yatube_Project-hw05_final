from django.db import models


class PubDateModel(models.Model):
    pub_date = models.DateTimeField(
        'Дата Публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
