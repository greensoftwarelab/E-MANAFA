import setuptools
from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='manafa',
    version='0.2.1',
    description='E-MANAFA: Energy Monitor and ANAlyzer For Android',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rui Rua',
    author_email='rui.rrua@gmail.com',
    url='https://github.com/RRua/e-manafa',
    license='MIT',
    #package_dir={"": "manafa"},
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
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
    ],
    project_urls = {
        'Bug Tracker':  'https://github.com/RRua/e-manafa/issues'
        },
    python_requires=">=3.8",
)

'''setup(
    name='e-manafa',
    version='0.1.0',
    packages=['tests', 'tests.perfetto', 'tests.batterystats', 'manafa', 'manafa.utils', 'manafa.perfetto',
              'manafa.services', 'manafa.batteryStats', 'manafa.powerProfile'],
    url='https://github.com/RRua/e-manafa',
    license='MIT',
    author='ruirua',
    author_email='rui.rrua@gmail.com',
    description='e-manafa tool'
)'''
