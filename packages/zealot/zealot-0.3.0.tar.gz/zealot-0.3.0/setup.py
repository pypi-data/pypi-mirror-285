from setuptools import setup
import os

VERSION = "0.3.0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="zealot",
    description="zealot is now django-zeal",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["django-zeal"],
    classifiers=["Development Status :: 7 - Inactive"],
    project_urls={"New package": "https://pypi.org/project/django-zeal/"},
)
