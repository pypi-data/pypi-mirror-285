from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory
from django.test.testcases import TestCase

from async_thumbnail import middleware


User = get_user_model()


class FetchFromCacheMiddlewareTestCase(TestCase):
    factory = RequestFactory()

    @patch("django.middleware.cache.FetchFromCacheMiddleware.process_request")
    def test_thumbnail_url_in_response(self, m):
        m.return_value = HttpResponse(content=b'<a href="/thumbnail/ABC/" />')
        request = self.factory.get("/")

        resp = middleware.FetchFromCacheMiddleware().process_request(request)
        assert resp is None
        assert request._cache_update_cache is True

        response = HttpResponse(content=b'<a href="/test/ABC/" />')
        m.return_value = response
        request = self.factory.get("/")

        resp = middleware.FetchFromCacheMiddleware().process_request(request)
        assert resp == response

    @patch("django.middleware.cache.FetchFromCacheMiddleware.process_request")
    def test_empty_response(self, m):
        m.return_value = None
        request = self.factory.get("/")
        middleware.FetchFromCacheMiddleware().process_request(request)
        assert request._cache_update_cache is True
