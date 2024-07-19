from setuptools import find_packages, setup
import os

def get_long_description():
    with open(
        os.path.join(os.path.dirname(__file__), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()

setup(
    name="koala-poder",
    packages=find_packages(include=['koala-poder']),
    version="0.1",
    description="A Python Library for generating sentences and doing math with koalas",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Blake Peterson",
    setup_requires=['pytest-runner'],
    tests_require=['pytest>=6.0.0'],
    test_suite='tests',
)
