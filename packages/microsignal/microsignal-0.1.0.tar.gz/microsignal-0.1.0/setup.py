from setuptools import setup, find_packages

setup(
    name='microsignal',
    version='0.1.0',
    packages=find_packages(),
    description='A lightweight library for handling custom signals with synchronous and asynchronous callbacks in Python.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tarasov Anton (taraant)',
    author_email='ant0@mail.ru',
    url='https://github.com/taraant/microsignal',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
