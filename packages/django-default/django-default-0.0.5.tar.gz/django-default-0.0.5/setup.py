import os

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-default",
    version="0.0.5",
    py_modules=["git_cloner"],
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "shinzo=git_cloner.git_cloner:clone_repo",
        ],
    },
    install_requires=[
        "alive_progress",
        "colorama",
        "black",
        "djangorestframework",
        "djangorestframework-simplejwt",
        "drf-spectacular",
        "drf-spectacular-sidecar",
        "Django",
        "django-jazzmin",
        "gunicorn",
        "pillow",
        "psycopg2-binary",
        "python-dotenv",
        "django-modeltranslation",
        "django-ckeditor-5",
        "django-cors-headers",
        "django-rosetta",
        "colorama",
        "PyJWT",
        "django-unfold",
        "django-redis",
        "celery",
        "flower",
    ],
    author="Jahongir Hakimjonov",
    author_email="jahongirhakimjonov@gmail.com",
    description="A Django project structure generator",
    keywords="django project structure generator",
    url="https://github.com/JahongirHakimjonov",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
)
