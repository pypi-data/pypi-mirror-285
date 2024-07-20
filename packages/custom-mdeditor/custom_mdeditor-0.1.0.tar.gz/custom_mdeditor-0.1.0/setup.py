from setuptools import setup, find_packages

setup(
    name="custom-mdeditor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Django>=3.0",

    ],
    include_package_data=True,
    description="A custom Django MD editor with modifications",
    long_description='k',
    long_description_content_type="text/markdown",
    url="https://github.com/Mahdi123408/mdeditor",
    author="Your Name",
    author_email="abasimahdi243@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
