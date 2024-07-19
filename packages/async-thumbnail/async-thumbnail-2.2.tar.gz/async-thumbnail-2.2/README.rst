***************
Async thumbnail
***************

.. image:: https://badge.fury.io/py/async-thumbnail.png
    :target: https://badge.fury.io/py/async-thumbnail

Offload sorl thumbnail rendering to a render view.

Installation
============

.. code-block:: sh

    pip install async-thumbnail


Usage
=====

.. note:: Make sure you have `sorl thumbnails <https://github.com/jazzband/sorl-thumbnail>`_ configured.

.. code-block:: python

        # settings.py
        INSTALLED_APPS = (
            # ...
            'async_thumbnail',
            # ...
        )

        # urls.py
        urlpatterns = [
            # ...
            path('', include('async_thumbnail.urls')),
            # ...
        ]


.. code-block:: html

    {% load async_thumbnail %}

    <!-- Default -->
    <img src="{% async_thumbnail object.image "900x600" crop="center" %}">

    <!-- Save as var -->
    {% async_thumbnail object.image "900x600" crop="center" as im %}
    <img src="{{ im.url }}" width="{{ im.width }}" height="{{ im.height }}">


FetchFromCacheMiddleware
------------------------

When you use the default full page caching middleware, it may be a good idea
to replace it with this middleware. This prevents cache from being updated when
the content contains a render URL.

.. warning:: In case you're using things like `source sets <https://www.w3schools.com/tags/att_source_srcset.asp>`_
    or lazy loading techniques this may be a bad idea.

.. code-block:: python

    # settings.py
    MIDDLEWARE = (
        'django.middleware.cache.UpdateCacheMiddleware',
        # ...
        'async_thumbnail.middleware.FetchFromCacheMiddleware',
    )


Settings
========

``ASYNC_THUMBNAIL_ENDPOINT``
----------------------------

- Default: ``''``

Optional setting to determine an absolute path for rendering.


``ASYNC_THUMBNAIL_PATTERN_NAME``
--------------------------------

- Default: ``'async_thumbnail:render'``

Pattern name for render URL's.

