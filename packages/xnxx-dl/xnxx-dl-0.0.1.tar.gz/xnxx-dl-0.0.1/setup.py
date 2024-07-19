from setuptools import setup, find_packages

setup(
    name='xnxx-dl',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
		'youtube-dl',
    ],
    author='Joannes J.A. Wyckmans',
    author_email='johan.wyckmans@gmail.com',
    description='A web scraping and URL filtering tool for xnxx.com',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/thisisawesome1994/xnxx-dl',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'web_scraper_app=app:main',
        ],
    },
    python_requires='>=3.6',
)