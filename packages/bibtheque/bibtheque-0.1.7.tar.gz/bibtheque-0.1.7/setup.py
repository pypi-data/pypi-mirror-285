from setuptools import setup, find_packages
import os

setup(
        packages=find_packages(),
        version=os.environ.get('VERSION'),
        install_requires=[
            'click',
            'pypdf',
            'bibtexparser',
            'habanero==1.2.3',
            'isbnlib',
            'numpy==1.26',
            'numba>=0.60.0',
            'pytest',
        ],
        entry_points={
            'console_scripts': [
                'bibtheque = bibtheque.cli:bibtheque',
            ]
        }
)
