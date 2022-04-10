from setuptools import find_packages, setup

docs_require = [
    "sphinx>=1.4.0",
]

tests_require = [
    "coverage[toml]==5.2",
    "pytest==7.0.1",
    "pytest-django==4.5.2",
    "requests-mock==1.9.3",
    "freezegun==1.2.1",
    # Linting
    "isort==5.10.1",
    "flake8==3.8.3",
    "flake8-blind-except==0.1.1",
    "flake8-debugger==3.2.1",
]

setup(
    name="django-healthchecks",
    version="1.4.2",
    description="Simple Django app/framework to publish health checks",
    long_description=open("README.rst", "r").read(),
    url="https://github.com/mvantellingen/django-healthchecks",
    author="Michael van Tellingen",
    author_email="michaelvantellingen@gmail.com",
    install_requires=[
        "Django>=2.2",
        "requests>=2.24.0",
        "certifi>=2020.6.20",
    ],
    tests_require=tests_require,
    extras_require={"docs": docs_require, "test": tests_require,},
    use_scm_version=True,
    entry_points={},
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    zip_safe=False,
)
