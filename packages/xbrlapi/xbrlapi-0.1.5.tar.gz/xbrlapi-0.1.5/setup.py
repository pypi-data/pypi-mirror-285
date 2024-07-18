# setup.py
from setuptools import setup, find_packages

setup(
    name='xbrlapi',
    version='0.1.5',  
    packages=find_packages(),
    install_requires=[
        'requests',
        'supabase',
        'pandas',
        'python-dotenv',
    ],
    author='Tomas Milo',
    author_email='tomas.sam.milo@gmail.com',
    description='A Python client for XBRLAPI',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TomasMiloCA/xbrlapi',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
