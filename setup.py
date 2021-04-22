import setuptools
from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='manafa',
    version='0.3.34',
    description='E-MANAFA: Energy Monitor and ANAlyzer For Android',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rui Rua',
    author_email='rui.rrua@gmail.com',
    url='https://github.com/RRua/e-manafa',
    license='MIT',
    packages=setuptools.find_packages(),
    install_requires=[
        'pytz==2021.1',
        'termcolor==1.1.0',
        'python-textops3==3.1.0',
        'python-dateutil==2.8.1',
        "setuptools>=42",
        "wheel"
    ],
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.8',
    ],
    project_urls={
        'Bug Tracker':  'https://github.com/RRua/e-manafa/issues'
        },
    python_requires=">=3.8",
)
