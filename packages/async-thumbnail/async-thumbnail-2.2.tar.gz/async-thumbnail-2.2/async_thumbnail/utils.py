import hashlib
import json
from urllib.parse import urljoin

from django.conf import settings
from django.core import signing
from django.core.cache import caches
from django.db.models.fields.files import ImageFieldFile
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.http import urlsafe_base64_encode
from PIL import Image
from sorl.thumbnail import default
from sorl.thumbnail.conf import defaults as default_settings
from sorl.thumbnail.images import ImageFile
from sorl.thumbnail.kvstores.base import add_prefix
from sorl.thumbnail.parsers import parse_geometry


def _get_setting(attr):
    return getattr(settings, attr, getattr(default_settings, attr))


def get_thumbnail(file_, geometry, **options):
    # Would be great if we could use the thumbnail backend for this, for now
    # its copied from default.backend.get_thumbnail(file_, geometry, **options)
    if file_:
        source = ImageFile(file_)
    else:
        raise ValueError("falsey file_ argument in get_thumbnail()")

    if _get_setting("THUMBNAIL_PRESERVE_FORMAT"):
        options.setdefault("format", default.backend._get_format(source))

    for key, value in default.backend.default_options.items():
        options.setdefault(key, value)

    for key, attr in default.backend.extra_options:
        value = _get_setting(attr)
        if value != getattr(default_settings, attr):
            options.setdefault(key, value)

    name = default.backend._get_thumbnail_filename(source, geometry, options)
    thumbnail = ImageFile(name, default.storage)
    cached = default.kvstore.get(thumbnail)

    if cached:
        return AsyncThumbnail(url=cached.url, cached=cached)

    token = signing.dumps(
        {
            "file": source.name,
            "geometry": geometry,
            "options": options,
            "storage": source.serialize_storage(),
        },
        salt="async_thumbnail.signing",
    )

    endpoint = getattr(settings, "ASYNC_THUMBNAIL_ENDPOINT", "")
    pattern_name = getattr(
        settings, "ASYNC_THUMBNAIL_PATTERN_NAME", "async_thumbnail:render"
    )

    base64_token = urlsafe_base64_encode(token.encode())
    if isinstance(base64_token, (bytes, bytearray)):
        base64_token = base64_token.decode()

    url = urljoin(endpoint, reverse(pattern_name, args=(base64_token,)))

    if isinstance(file_, ImageFieldFile):
        if file_.field.width_field and file_.field.height_field:
            width = getattr(file_.instance, file_.field.width_field, None)
            height = getattr(file_.instance, file_.field.height_field, None)
            if width and height:
                source.set_size((width, height))
    return AsyncThumbnail(url=url, source=source, geometry=geometry, options=options)


class AsyncThumbnail:
    def __init__(self, url, source=None, cached=None, geometry=None, options=None):
        super().__init__()
        self.url = url
        source = source
        self.source = source
        self.cached = cached
        self.geometry = geometry

        self.options = options or {}
        self._cache = caches[_get_setting("THUMBNAIL_CACHE")]

    def __str__(self):
        return self.url

    @cached_property
    def size(self):
        return self.get_size()

    def get_size(self):
        if hasattr(self.cached, "_size"):
            return self.cached._size
        self.source.set_size()

        ratio = default.engine.get_image_ratio(self.source, self.options)
        geometry = parse_geometry(self.geometry, ratio)
        size = default.engine.get_image_size(self.source)

        options_hash = hashlib.sha1(
            json.dumps(
                {"geometry": geometry, "size": size, "options": self.options},
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()

        cache_identifier = add_prefix(options_hash, "image_size")
        image_size = self._cache.get(cache_identifier)

        if not image_size:
            image = Image.new("RGB", size, (255, 255, 255))
            image = default.engine.cropbox(image, geometry, self.options)
            image = default.engine.scale(image, geometry, self.options)
            image = default.engine.crop(image, geometry, self.options)
            image = default.engine.padding(image, geometry, self.options)
            image_size = default.engine.get_image_size(image)
            self._cache.set(cache_identifier, image_size)

        return image_size

    @cached_property
    def width(self):
        return self.size[0]

    @cached_property
    def height(self):
        return self.size[1]
