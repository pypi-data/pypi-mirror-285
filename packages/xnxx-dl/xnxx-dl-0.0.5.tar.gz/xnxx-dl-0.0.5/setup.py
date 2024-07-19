from setuptools import setup, find_packages

def read_long_description():
    try:
        with open('README.md', 'r', encoding='utf-8') as fh:
            return fh.read()
    except FileNotFoundError:
        return 'A web scraping and URL filtering tool for xnxx.com'
        
setup(
    name='xnxx-dl',
    version='0.0.5',
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
            'xnxx-dl.py=main',
        ],
    },
    python_requires='>=3.6',
)