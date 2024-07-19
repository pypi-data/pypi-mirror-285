from django.core import signing
from django.test import override_settings
from django.test.testcases import TestCase
from django.utils.http import urlsafe_base64_decode

from async_thumbnail.templatetags.async_thumbnail import async_thumbnail

from .helpers import MediaRootMixin


class AsyncThumbnailTestCase(MediaRootMixin, TestCase):
    def _extract_values_from_token(self, url):
        token = url.strip("/").split("/")[-1]
        return signing.loads(
            urlsafe_base64_decode(token).decode(), salt="async_thumbnail.signing"
        )

    @override_settings(THUMBNAIL_DUMMY=False)
    def test_empty_file_no_dummy(self):
        assert async_thumbnail("", "100x100") == ""

    @override_settings(THUMBNAIL_DUMMY=True)
    def test_empty_file_dummy(self):
        assert async_thumbnail("", "100x10").url == "http://dummyimage.com/100x10"

    @override_settings(THUMBNAIL_PRESERVE_FORMAT=True)
    def test_preserve_format_true(self):
        result = {
            "file": "test.jpg",
            "geometry": "100x100",
            "options": {
                "colorspace": "RGB",
                "crop": False,
                "cropbox": None,
                "format": "JPEG",
                "padding": False,
                "padding_color": "#ffffff",
                "quality": 95,
                "rounded": None,
                "upscale": True,
            },
            "storage": "django.core.files.storage.FileSystemStorage",
        }

        assert (
            self._extract_values_from_token(async_thumbnail("test.jpg", "100x100").url)
            == result
        )

        result["file"] = "test.jpeg"

        assert (
            self._extract_values_from_token(async_thumbnail("test.jpeg", "100x100").url)
            == result
        )

        result["file"] = "test.png"
        result["options"]["format"] = "PNG"

        assert (
            self._extract_values_from_token(async_thumbnail("test.png", "100x100").url)
            == result
        )

        result["file"] = "test.gif"
        result["options"]["format"] = "GIF"

        assert (
            self._extract_values_from_token(async_thumbnail("test.gif", "100x100").url)
            == result
        )

    @override_settings(THUMBNAIL_PRESERVE_FORMAT=False)
    def test_preserve_format_false(self):
        result = {
            "file": "test.jpg",
            "geometry": "100x100",
            "options": {
                "colorspace": "RGB",
                "crop": False,
                "cropbox": None,
                "format": "JPEG",
                "padding": False,
                "padding_color": "#ffffff",
                "quality": 95,
                "rounded": None,
                "upscale": True,
            },
            "storage": "django.core.files.storage.FileSystemStorage",
        }

        assert (
            self._extract_values_from_token(async_thumbnail("test.jpg", "100x100").url)
            == result
        )

        result["file"] = "test.jpeg"

        assert (
            self._extract_values_from_token(async_thumbnail("test.jpeg", "100x100").url)
            == result
        )

        result["file"] = "test.png"

        assert (
            self._extract_values_from_token(async_thumbnail("test.png", "100x100").url)
            == result
        )

        result["file"] = "test.gif"

        assert (
            self._extract_values_from_token(async_thumbnail("test.gif", "100x100").url)
            == result
        )

    @override_settings(THUMBNAIL_PROGRESSIVE=True)
    def test_extra_options_default_value(self):
        result = {
            "file": "test.jpg",
            "geometry": "100x100",
            "options": {
                "colorspace": "RGB",
                "crop": False,
                "cropbox": None,
                "format": "JPEG",
                "padding": False,
                "padding_color": "#ffffff",
                "quality": 95,
                "rounded": None,
                "upscale": True,
            },
            "storage": "django.core.files.storage.FileSystemStorage",
        }

        assert (
            self._extract_values_from_token(async_thumbnail("test.jpg", "100x100").url)
            == result
        )

    @override_settings(THUMBNAIL_PROGRESSIVE=False)
    def test_extra_options_different_value(self):
        result = {
            "file": "test.jpg",
            "geometry": "100x100",
            "options": {
                "colorspace": "RGB",
                "crop": False,
                "cropbox": None,
                "format": "JPEG",
                "padding": False,
                "padding_color": "#ffffff",
                "quality": 95,
                "rounded": None,
                "upscale": True,
                "progressive": False,
            },
            "storage": "django.core.files.storage.FileSystemStorage",
        }

        assert (
            self._extract_values_from_token(async_thumbnail("test.jpg", "100x100").url)
            == result
        )

    @override_settings(MEDIA_ROOT=MediaRootMixin.MEDIA_ROOT)
    def test_cached(self):
        result = {
            "file": "test.jpg",
            "geometry": "100x100",
            "options": {
                "colorspace": "RGB",
                "crop": False,
                "cropbox": None,
                "format": "JPEG",
                "padding": False,
                "padding_color": "#ffffff",
                "quality": 95,
                "rounded": None,
                "upscale": True,
            },
            "storage": "django.core.files.storage.FileSystemStorage",
        }

        url = async_thumbnail("test.jpg", "100x100").url
        assert self._extract_values_from_token(url) == result
        resp = self.client.get(url)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

        assert (
            async_thumbnail("test.jpg", "100x100").url.strip("/")
            == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"
        )
