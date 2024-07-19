import shutil
from os import environ
from os.path import abspath, dirname, exists, join


class MediaRootMixin(object):
    MEDIA_ROOT = abspath(
        join(dirname(__file__), environ.get("PYTEST_XDIST_WORKER", ""), "media")
    )

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        if not exists(cls.MEDIA_ROOT):
            shutil.copytree(abspath(join(dirname(__file__), "data")), cls.MEDIA_ROOT)

    def setUp(self):
        super().setUp()
        thumbnails = join(self.MEDIA_ROOT, "cache")
        if exists(thumbnails):
            shutil.rmtree(thumbnails)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.MEDIA_ROOT)

        if environ.get("PYTEST_XDIST_WORKER", ""):
            shutil.rmtree(abspath(join(cls.MEDIA_ROOT, "..")))
