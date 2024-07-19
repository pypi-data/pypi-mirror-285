import django

from . import views


app_name = "async_thumbnail"

if django.VERSION < (2, 0):
    from django.conf.urls import url

    urlpatterns = [
        url(r"^thumbnail/(?P<token>[^/]+)/$", views.thumbnail_view, name="render")
    ]
else:
    from django.urls import path

    urlpatterns = [path("thumbnail/<token>/", views.thumbnail_view, name="render")]
