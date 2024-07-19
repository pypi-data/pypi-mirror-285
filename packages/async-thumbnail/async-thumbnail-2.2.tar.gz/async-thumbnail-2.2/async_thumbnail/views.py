from django.conf import settings
from django.core import signing
from django.core.exceptions import ImproperlyConfigured
from django.core.signing import BadSignature
from django.http import Http404, HttpResponseBadRequest
from django.http.response import HttpResponsePermanentRedirect
from django.utils.http import urlsafe_base64_decode
from sorl.thumbnail import default
from sorl.thumbnail.helpers import get_module_class
from sorl.thumbnail.images import ImageFile


def thumbnail_view(request, token):
    try:
        data = signing.loads(
            urlsafe_base64_decode(token).decode(), salt="async_thumbnail.signing"
        )
    except (ValueError, BadSignature):
        return HttpResponseBadRequest("Invalid token.")

    try:
        storage = get_module_class(data["storage"])()
    except (AttributeError, ImproperlyConfigured):
        storage = None
    source = ImageFile(data["file"], storage)
    geometry_string = data["geometry"]
    options = data["options"]

    name = default.backend._get_thumbnail_filename(source, geometry_string, options)
    thumbnail = ImageFile(name, default.storage)
    cached = default.kvstore.get(thumbnail)

    if cached:
        return HttpResponsePermanentRedirect(cached.url)

    if getattr(settings, "THUMBNAIL_FORCE_OVERWRITE", False) or not thumbnail.exists():
        try:
            source_image = default.engine.get_image(source)
        except IOError:
            raise Http404(
                f'Remote file [{data["file"]}] at '
                f"[{geometry_string}] does not exist"
            )

        image_info = default.engine.get_image_info(source_image)
        options["image_info"] = image_info
        size = default.engine.get_image_size(source_image)
        source.set_size(size)

        try:
            default.backend._create_thumbnail(
                source_image, geometry_string, options, thumbnail
            )
            default.backend._create_alternative_resolutions(
                source_image, geometry_string, options, thumbnail.name
            )
        finally:
            default.engine.cleanup(source_image)

    default.kvstore.get_or_set(source)
    default.kvstore.set(thumbnail, source)
    return HttpResponsePermanentRedirect(thumbnail.url)
