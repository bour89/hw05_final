from django.db import models


class CreatedTimeModel(models.Model):

    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        # Это абстрактная модель:
        abstract = True
