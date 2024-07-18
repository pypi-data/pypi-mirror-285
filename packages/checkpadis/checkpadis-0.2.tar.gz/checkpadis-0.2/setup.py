from setuptools import setup, find_packages

setup(
    name='checkpadis',
    version='0.2',
    packages=find_packages(),
    author='PADIS',
    description='Viabilidad 01',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'click',
        'colorama',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'checkpadis=checkpadis.cli:checkpadis',
        ],
    },
)