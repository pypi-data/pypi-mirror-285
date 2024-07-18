from setuptools import find_packages, setup

# This is the setup.py file for our SDK.
# It is used to package deeptune SDK and upload it to PyPI.
# Copy this into the fern generated SDK repo, bump the version number,
# and run the following commands:
# mkdir sdks/python/deeptune && \
# mv sdks/python/core sdks/python/deeptune && \
# mv sdks/python/errors sdks/python/deeptune && \
# mv sdks/python/text_to_speech sdks/python/deeptune && \
# mv sdks/python/types sdks/python/deeptune && \
# mv sdks/python/voices sdks/python/deeptune && \
# mv sdks/python/__init__.py sdks/python/deeptune && \
# mv sdks/python/client.py sdks/python/deeptune && \
# mv sdks/python/environment.py sdks/python/deeptune && \
# cd sdks/python && \
# python setup.py sdist bdist_wheel && \
# twine upload dist/*
#
# put in your pypi API key to proceed with the upload

setup(
    name="deeptune",  # This should be the name of your package
    version="0.1.18",
    description="Python SDK for Deeptune Text-to-Speech API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Deeptunee",
    author_email="blair@deeptune.com",
    url="https://github.com/yourusername/blair-wdq",  # Update this URL to your repository
    packages=find_packages(
        include=["deeptune", "deeptune.*"]
    ),  # Adjust this if your package structure is different
    install_requires=[
        "requests",  # Add other dependencies if necessary
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
