from setuptools import setup, find_packages
from monkey import __version__

setup(
    name='monkey-cli',
    version=__version__,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    entry_points={
        'console_scripts': [
            'monkey=monkey.__main__:main',
        ],
    },
    install_requires=[
        # Add your dependencies here
    ],
)
