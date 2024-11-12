from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="celery-valkey-backend",
    version="0.1.0",
    author="vuonglv",
    author_email="it.vuonglv@gmail.com",
    description="A custom Celery result backend using Valkey as the storage engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vuonglv1612/celery-valkey-backend",
    project_urls={
        "Bug Tracker": "https://github.com/vuonglv1612/celery-valkey-backend/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    package_dir={"": "celery_valkey_backend"},
    packages=find_packages(where="celery_valkey_backend"),
    python_requires=">=3.7",
    install_requires=[
        "celery>=4.4.0",
        "valkey>=6.0.0",
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'flake8>=4.0.0',
            'mypy>=0.900',
            'tox>=3.24.0',
            'testcontainers>=3.7.1',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'celery.result_backends': [
            'valkey = celery_valkey_backend.valkey_backend:ValKeyBackend',
        ],
    },
)