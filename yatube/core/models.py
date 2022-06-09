from django.db import models


class CreatedTimeModel(models.Model):
    #created = models.DateTimeField(
    #    'Дата создания',
    #    auto_now_add=True
    #)
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        # Это абстрактная модель:
        abstract = True

