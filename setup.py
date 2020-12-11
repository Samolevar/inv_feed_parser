from pathlib import Path
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()


def requirements():
    path = Path.cwd().joinpath('requirements.txt')
    if not path.is_file():
        return []
    with path.open() as rq:
        return [req for req in rq.readlines()]


if __name__ == '__main__':
    setup(
        name="rss_feed_parser", # Replace with your own username
        version="0.0.1",
        author="Denis Aminev",
        author_email="daminev@gmail.com",
        description="A small package for parse rss feed by stock's name of a company",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="not ready yet",
        install_requires=requirements(),
        packages=['rss_feed_parser'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.7',
)
