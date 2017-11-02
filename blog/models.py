from django.db import models
from django.contrib.auth.models import User


class Article(models.Model):
    title = models.CharField(max_length=64)
    content = models.TextField()
    author = models.ForeignKey(
        User,
        related_name='articles', # 불필요할 수도
        null=False
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        User,
        related_name='comments',
        null=True
    )
    article = models.ForeignKey(
        Article,
        related_name='comments',
        null=True
    )

