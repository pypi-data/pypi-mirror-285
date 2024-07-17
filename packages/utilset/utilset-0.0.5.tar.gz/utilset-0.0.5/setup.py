from setuptools import setup
from os import path

print(path.abspath(path.dirname(__file__)))
with open(
        path.join(path.abspath(path.dirname(__file__)), 'README.md'),
        encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='utilset',
    version='0.0.5',
    author='puresai',
    author_email='sai210728@gmail.com',
    url='https://github.com/puresai/utilset',
    description="util sets",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=['utilset'],
    install_requires=[],
    platforms=["all"],
    classifiers=[
        'Intended Audience :: Developers', 'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries'
    ],
)
