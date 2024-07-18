from setuptools import setup, find_packages

setup(
    name='SimpleColorLogger',
    version='1.4',
    packages=find_packages(),
    description='A simple colored logger for terminal output',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Tim Lukas Tritschler',
    author_email='info@music-request.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
