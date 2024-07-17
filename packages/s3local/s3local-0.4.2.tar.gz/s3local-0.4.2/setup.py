from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
install_requires = ["boto3", "click>=7.0"]
extras_require = {"test": ["tox"]}

setup(
    name="s3local",
    version="0.4.2",
    description="Command Line utility for s3 local caching.",
    long_description=open(os.path.join(here, "README.md")).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="s3local tool aws s3",
    author="Hiroshi Toyama",
    author_email="toyama0919@gmail.com",
    url="https://github.com/toyama0919/s3local",
    license="MIT",
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=extras_require["test"],
    entry_points={"console_scripts": ["s3local=s3local.commands:main"]},
)
