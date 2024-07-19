from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ggfile_sorter',
    version='0.2.0',
    author='gthth',
    author_email='firi8228@gmail.com',
    description='A tool for sorting files into categories based on their extensions',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['file_sorter'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)