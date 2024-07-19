import re
import urllib

from django.conf import settings
from django.middleware.cache import (
    FetchFromCacheMiddleware as DjangoFetchFromCacheMiddleware,
)
from django.urls import reverse


class FetchFromCacheMiddleware(DjangoFetchFromCacheMiddleware):
    def process_request(self, request):
        response = super().process_request(request)
        pattern_name = getattr(
            settings, "ASYNC_THUMBNAIL_PATTERN_NAME", "async_thumbnail:render"
        )
        url = reverse(pattern_name, args=("[A-z0-9-_=]*",))
        if response is None or re.search(
            urllib.parse.unquote(url), response.content.decode(), re.MULTILINE
        ):
            request._cache_update_cache = True
            return None
        return response
