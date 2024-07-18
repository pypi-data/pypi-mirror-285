from setuptools import setup, find_packages

setup(
    name='gdbot',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'requests'
    ],
    author='SevenworksDev',
    author_email='mail@sevenworks.eu.org',
    description='Python Library for creating Geometry Dash Comment Bots.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SevenworksDev/GDBotPy',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)