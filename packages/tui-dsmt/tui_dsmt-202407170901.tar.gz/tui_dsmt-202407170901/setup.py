from setuptools import setup, find_packages
from datetime import datetime


version = datetime.now().strftime('%Y%m%d%H%M')

setup(
    name='tui_dsmt',
    version=version,
    author='Eric Tröbs',
    author_email='eric.troebs@tu-ilmenau.de',
    description='everything you need for our jupyter notebooks',
    long_description='everything you need for our jupyter notebooks',
    long_description_content_type='text/markdown',
    url='https://dbgit.prakinf.tu-ilmenau.de/lectures/data-science-methoden-und-techniken',
    project_urls={},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.10',
    install_requires=[
        'jupyter',
        'ipywidgets',
        'checkmarkandcross',
        'fa2_modified~=0.3.10',
        'ipyparallel~=8.8.0',
        'matplotlib~=3.8.4',
        'mlxtend~=0.23.1',
        'mpi4py~=3.1.6',
        'networkx~=3.2.1',
        'plotly~=5.20.0',
        'pandas~=2.2.1',
        'pyarrow~=15.0.2',
        'pyfpgrowth~=1.0',
        'pyspark~=3.5.1',
        'scikit-learn~=1.4.2',
        'scikit-learn-extra~=0.3.0'
    ],
    package_data={
        'tui_dsmt': [
            'jpanim/resources/*',
            'fpm/resources/*',
            'graph/resources/*',
            'parallel/resources/*',
        ]
    },
    include_package_data=True
)
