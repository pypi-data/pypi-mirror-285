from distutils.core import setup
from setuptools import find_packages
from __version__ import main_version, medium_version, minor_version

with open("README.rst", "r" , encoding="utf-8") as f:
    long_description = f.read()
    minor_version = minor_version + 1
    with open('__version__.py', 'w+') as f:
        f.write(f'main_version = "{main_version}"\n')
        f.write(f'medium_version = "{medium_version}"\n')
        f.write(f'minor_version = "{minor_version}"\n')
    
    setup(
        name='cukoo_fastapi_addto',
        version=f'{main_version}.{medium_version}.{minor_version}',
        description='framework addto for fastapi',
        long_description=long_description,
        author='phailin',
        author_email='phailin791@hotmail.com',
        url='https://github.com/phailin/cukoo_fastapi_addto',
        install_requires=[
            "fastapi>=0.111.1",
            "SQLAlchemy>=2.0.31",
            "pydantic>=2.8.2",
            "loguru>=0.7.2",
            "python-jose[cryptography]>=3.3.0",
            "passlib>=1.7.4",
            "bcrypt>=4.0.1",
            "python-multipart>=0.0.9",
        ],
        license='MIT',
        packages=find_packages(),
        platforms=["all"],
        classifiers=[
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Natural Language :: Chinese (Simplified)',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Topic :: Software Development :: Libraries'
        ],
    )