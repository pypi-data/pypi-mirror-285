from django import template
from sorl.thumbnail.images import DummyImageFile

from async_thumbnail.utils import _get_setting, get_thumbnail


register = template.Library()


@register.simple_tag()
def async_thumbnail(file_, geometry, **options):
    thumbnail = ""
    if file_:
        thumbnail = get_thumbnail(file_, geometry, **options)
    elif _get_setting("THUMBNAIL_DUMMY"):
        thumbnail = DummyImageFile(geometry)

    return thumbnail
