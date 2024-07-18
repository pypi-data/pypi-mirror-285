from setuptools import setup, find_packages

# Читаем файл README.md для длинного описания
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django_logger_clickhouse",
    version="0.1.2",
    author="Алексей",
    author_email="vipzenit666@yandex.ru",
    description="Логгер Django для ClickHouse с Celery.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/single-service/clickhouse_django_logger",
    # project_urls={
    #     "Homepage": "https://github.com/single-service/clickhouse_django_logger",
    #     "Issues": "https://github.com/single-service/clickhouse_django_logger/issues",
    # },
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="MIT",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.6",
    install_requires=[
        "Django>=2.2",
        "celery>=5.0",
        "requests>=2.0",
    ],
    extras_require={
        "dev": ["pytest", "mypy", "flake8"],
        "docs": ["sphinx"],
    },
    include_package_data=True,
    zip_safe=False,
)
