from django.conf.urls import url
from blog import views

urlpatterns = [
    url('^signup$', views.signup, name='signup'),
    url('^token$', views.token, name='token'),
    url('^article$', views.articleList, name='articleList'),
    url('^article/(?P<article_id>[0-9]+)$', views.articleDetail, name='articleDetail'),
    url('^article/(?P<article_id>[0-9]+)/comment', views.commentList, name='commentList'),
    url('^comment/(?P<comment_id>[0-9]+)$', views.commentDetail, name='commentDetail'),
]
