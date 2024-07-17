from setuptools import find_packages, setup

with open('readme.md', 'r') as readme:
    long_description = readme.read()

setup(
    name = 'tokenbuffer',
    version = '0.1.4',
    description = 'A tokenizer with file position tracking and backtracking suitable for making parsers.',
    package_dir = {"": "src"},
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'pawkw',
    url = 'https://github.com/pawkw/tokenbuffer',
    license = 'MIT',
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent'
    ],
    extras_require = {
        "dev": ['twine>=5.1.1'],
    },
    python_requires = '>=3.10'
)