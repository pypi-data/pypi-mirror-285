from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ez-convert",
    version="0.1.0",
    author="Malek Ibrahim",
    author_email="shmeek8@gmail.com",
    description="A simple command line tool to convert files from one form to another.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/malekinho8/ez-convert",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'click',
        'pyperclip',
        'Pillow',
        'moviepy'
    ],
    entry_points='''
        [console_scripts]
        ezconvert=ez_convert.main:main
    ''',
)