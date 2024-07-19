import os

from Cython.Build import cythonize
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as file:
    content = file.read()


def find_python_files(directory):
    return [os.path.join(root, file)
            for root, dirs, files in os.walk(directory)
            for file in files
            if file.endswith('.py') and not file.startswith('__init__')]


setup(
    name='locobuzz_python_orm',
    version='1.0.4',
    author="Atharva Udavant",
    author_email="atharva.udavant@locobuzz.com",
    packages=find_packages(),
    ext_modules=cythonize(find_python_files("locobuzz_python_orm")),
    install_requires=[
        'Cython',
    ],
    extras_require={
        'dataframe': ['pandas']
    },
    keywords=['locobuzz', 'python', 'database'],
    url="https://github.com/LocoBuzz-Solutions-Pvt-Ltd/locobuzz_database_orm",
    description="Python database orm functions for Locobuzz,  common code that is required in all projects",
    long_description=content,
    long_description_content_type="text/markdown",
    python_requires=">=3.8, <=3.12",
    test_suite='tests',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",

        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
