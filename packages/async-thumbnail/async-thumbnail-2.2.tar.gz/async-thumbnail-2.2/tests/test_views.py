from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.test import override_settings
from django.test.testcases import TestCase
from django.utils.http import urlsafe_base64_encode
from sorl.thumbnail import default

from async_thumbnail.templatetags.async_thumbnail import async_thumbnail
from async_thumbnail.views import thumbnail_view

from .helpers import MediaRootMixin


@override_settings(MEDIA_ROOT=MediaRootMixin.MEDIA_ROOT)
class AsyncThumbnailTestCase(MediaRootMixin, TestCase):
    def _get_token(self, filename, geometry, **options):
        url = async_thumbnail(filename, geometry, **options).url
        return url.strip("/").split("/")[-1]

    def test_token_extraction(self):
        token = self._get_token("test.jpg", "100x100")
        resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

        resp = thumbnail_view({}, "ABC")
        assert resp.status_code == 400
        assert resp.content == b"Invalid token."

        bad_signature = urlsafe_base64_encode(b"test")
        if isinstance(bad_signature, (bytes, bytearray)):
            bad_signature = bad_signature.decode()

        resp = thumbnail_view({}, bad_signature)
        assert resp.status_code == 400
        assert resp.content == b"Invalid token."

    def test_cached(self):
        token = self._get_token("test.jpg", "100x100")

        with self.assertNumQueries(16):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

        with self.assertNumQueries(1):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

        token = self._get_token("test.jpg", "100x10")

        with self.assertNumQueries(10):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/f9/26/f926e5e2d029b3710abcf6e7d4cedb45.jpg"

        with self.assertNumQueries(1):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/f9/26/f926e5e2d029b3710abcf6e7d4cedb45.jpg"

    @override_settings(THUMBNAIL_FORCE_OVERWRITE=True)
    def test_force_overwrite_true(self):
        token = self._get_token("test.jpg", "100x100")

        with self.assertNumQueries(16):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

        default.kvstore.clear()

        with self.assertNumQueries(16):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") != "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"
        assert resp.url.strip("/").startswith(
            "cache/53/88/53889dfdb53708f95d264fa36fb45c22"
        )

    @override_settings(THUMBNAIL_FORCE_OVERWRITE=False)
    def test_force_overwrite_false(self):
        token = self._get_token("test.jpg", "100x100")

        with self.assertNumQueries(16):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

        default.kvstore.clear()

        with self.assertNumQueries(16):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

    def test_non_existing_file(self):
        token = self._get_token("test-404.jpg", "100x100")

        with self.assertRaisesMessage(
            Http404, "Remote file [test-404.jpg] at [100x100] does not exist"
        ):
            resp = thumbnail_view({}, token)
            assert resp.status_code == 404
            assert resp.content == b""

    def test_token_with_invalid_storage(self):
        token = self._get_token("test.jpg", "100x100")
        with patch(
            "async_thumbnail.views.get_module_class", side_effect=AttributeError
        ):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"

        with patch(
            "async_thumbnail.views.get_module_class", side_effect=ImproperlyConfigured
        ):
            resp = thumbnail_view({}, token)
        assert resp.status_code == 301
        assert resp.url.strip("/") == "cache/53/88/53889dfdb53708f95d264fa36fb45c22.jpg"
