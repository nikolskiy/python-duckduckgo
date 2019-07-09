from setuptools import setup
import sys


MIN_PYTHON = (3, 7)
if sys.version_info < MIN_PYTHON:
    sys.exit("Python %s.%s or later is required.\n" % MIN_PYTHON)


with open("README.rst", "r") as fh:
    long_description = fh.read()


VERSION = '0.0.1'


setup(
    python_requires='>=3.7',
    name='duckduckgoapi',
    version=VERSION,
    py_modules=['duckduckgo'],
    description='Library for querying the DuckDuckGo API',
    author='Denis Nikolskiy',
    license='BSD',
    url='http://github.com/nikolskiy/python-duckduckgo/',
    long_description=long_description,
    platforms=['any'],
    install_requires=['marshmallow>=3.0'],
    keywords='duckduckgo quick answer',
    classifiers=[
        "Development Status :: Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    entry_points={'console_scripts': ['ddg = duckduckgo:main']},)
