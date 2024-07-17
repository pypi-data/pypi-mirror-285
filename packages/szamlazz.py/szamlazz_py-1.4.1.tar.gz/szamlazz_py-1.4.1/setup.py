import setuptools
from datetime import datetime
from szamlazz.version import get_git_version


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="szamlazz.py",
    version=get_git_version(),
    author='Kristof Daja (theriverman)',
    author_email='cowling_benzene0r@icloud.com',
    description='Python client for Szamlazz.hu :: Számla Agent',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/theriverman/szamlazz.py',
    project_urls={
        "Bug Tracker": "https://github.com/theriverman/szamlazz.py/issues",
    },
    install_requires=[
        'Jinja2~=3.1.2',
        'requests>=2.31.0',
        'lxml~=4.9.2',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    license=f'MIT License | Copyright (c) 2020 — {datetime.now().year} Kristof Daja',
)
