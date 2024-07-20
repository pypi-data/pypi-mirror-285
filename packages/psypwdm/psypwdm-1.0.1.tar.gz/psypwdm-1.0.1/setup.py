from setuptools import setup
from psypwdm import __version__
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

if __name__ == '__main__':
    setup(
        name='psypwdm',
        description='An open source, local password manager written with python for postgres',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/KshkB/local-password-manager',
        author='Kowshik Bettadapura',
        author_email='k.bettad@gmail.com',
        packages=['psypwdm'],
        version=f'{__version__}',
        license='MIT',
        include_package_data=True
    )

