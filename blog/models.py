from django.db import models


class User(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=16)

    def __str__(self):
        return self.username


class Article(models.Model):
    title = models.CharField(max_length=64)
    content = models.TextField()
    author_id = models.IntegerField()
    author = models.ForeignKey(
        User,
        related_name='articles', # 불필요할 수도
        null=False
    )

    def __str__(self):
        return self.title


class Comment(models.Model):
    article_id = models.IntegerField()
    content = models.TextField()
    author_id = models.IntegerField()
    article = models.ForeignKey(
        Article,
        related_name='comments',
        null=True
    )

