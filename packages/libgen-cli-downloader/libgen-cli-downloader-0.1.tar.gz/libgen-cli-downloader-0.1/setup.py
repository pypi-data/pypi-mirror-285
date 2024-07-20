from setuptools import setup, find_packages

setup(
    name='libgen-cli-downloader',
    version='0.1',
    author='Ali Koçak',
    author_email='kocakali5834@gmail.com',
    description='Command line tool to search and download books from libgen',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'libdown = main:main'
        ]
    },
    classifiers=[
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'beautifultable',
        'requests',
        'tqdm',
        'lxml',
        'beautifulsoup4'
    ]
)