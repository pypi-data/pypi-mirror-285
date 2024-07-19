from setuptools import setup, find_packages

import ratelimit


with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="ratelimit-extended",
    version=ratelimit.__version__,
    description="API rate limit decorator",
    long_description=long_description,
    author="Ömer Faruk Yığın",
    author_email="omert1122@gmail.com",
    url="https://github.com/omert11/ratelimit",
    license="MIT",
    packages=find_packages(),
    install_requires=[],
    keywords=["ratelimit", "api", "decorator"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Software Development",
    ],
    include_package_data=True,
    zip_safe=False,
)
