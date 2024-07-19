#!/usr/bin/env python

from setuptools import find_packages, setup


version = "2.2"

setup(
    name="async-thumbnail",
    packages=find_packages(),
    version=version,
    description="Offload sorl thumbnail rendering to a render view.",
    long_description=open("README.rst").read(),
    author="Sven Groot (Mediamoose)",
    author_email="sven@mediamoose.nl",
    url="https://gitlab.com/mediamoose/async-thumbnail/tree/v{}".format(version),
    download_url="https://gitlab.com/mediamoose/async-thumbnail/repository/v{}/archive.tar.gz".format(
        version
    ),
    include_package_data=True,
    install_requires=["django>=1.11", "sorl-thumbnail>=12.5.0", "pillow>=5.3.0"],
    license="MIT",
    zip_safe=False,
    keywords=["async", "asynchronous", "thumbnail", "sorl", "django"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
