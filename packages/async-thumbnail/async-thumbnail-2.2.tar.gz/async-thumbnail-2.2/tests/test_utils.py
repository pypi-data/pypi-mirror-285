import hashlib
import json
from unittest.mock import patch

from django.core.cache.backends.locmem import LocMemCache
from django.test import override_settings
from django.test.testcases import TestCase
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.kvstores.base import add_prefix

from async_thumbnail import utils
from async_thumbnail.templatetags.async_thumbnail import async_thumbnail

from .helpers import MediaRootMixin


@override_settings(MEDIA_ROOT=MediaRootMixin.MEDIA_ROOT)
class AsyncThumbnailTestCase(MediaRootMixin, TestCase):
    class DummyCached:
        _size = (100, 100)

    def check_thumbnails(self, geometry="400x300", **options):
        source = ImageFile("test.jpg")
        async_thumb = async_thumbnail(source, geometry, **options)
        thumbnail = get_thumbnail("test.jpg", geometry, **options)
        self.assertEqual(thumbnail.x, async_thumb.width)
        self.assertEqual(thumbnail.y, async_thumb.height)

    def test_thumbnail_size(self):
        self.check_thumbnails(crop="center")
        self.check_thumbnails(crop="13% 80%")
        self.check_thumbnails(upscale=False)
        self.check_thumbnails(upscale=True)
        self.check_thumbnails(crop="center", upscale=False)
        self.check_thumbnails(crop="center", upscale=True)
        self.check_thumbnails(crop="center", padding=True, upscale=False)
        self.check_thumbnails(crop="center", padding=True, upscale=True)
        self.check_thumbnails(crop="30% 40%", padding=True, upscale=True)
        self.check_thumbnails(geometry="50x600", upscale=False)
        self.check_thumbnails(geometry="50x600", crop="center", upscale=False)

    def test_cached(self):
        async_thumb = utils.AsyncThumbnail(url="test.png", cached=self.DummyCached())
        assert async_thumb.width == 100
        assert async_thumb.height == 100

    def test_str(self):
        assert str(utils.AsyncThumbnail(url="test.png")) == "test.png"

    def test_cached_result(self):
        locmem_cache = LocMemCache(self.__class__.__name__, {})
        locmem_cache.clear()
        source = ImageFile("test.jpg")
        async_thumb = async_thumbnail(source, "400x300", crop="center")

        with patch.object(async_thumb, "_cache", locmem_cache):
            options_hash = hashlib.sha1(
                json.dumps(
                    {
                        "geometry": (400, 300),
                        "size": [100, 100],
                        "options": async_thumb.options,
                    },
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            cache_identifier = add_prefix(options_hash, "image_size")
            assert cache_identifier not in locmem_cache
            async_thumb.get_size()
            assert cache_identifier in locmem_cache
            assert async_thumb.get_size() == locmem_cache.get(cache_identifier)

    def test_get_thumbnail(self):
        with self.assertRaises(ValueError):
            utils.get_thumbnail(None, "100x100")
