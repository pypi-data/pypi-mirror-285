from setuptools import setup, find_packages
from datetime import datetime


version = datetime.now().strftime('%Y%m%d%H%M')

setup(
    name='tui_dsg',
    version=version,
    author='Eric Tröbs',
    author_email='eric.troebs@tu-ilmenau.de',
    description='everything you need for our jupyter notebooks',
    long_description='everything you need for our jupyter notebooks',
    long_description_content_type='text/markdown',
    url='https://dbgit.prakinf.tu-ilmenau.de/lectures/data-science-grundlagen',
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
        'beautifulsoup4~=4.12.3',
        'fa2_modified',
        'grizzly_sql==0.1.5.post1',
        'HanTa~=1.1.1',
        'kaleido~=0.2.1',
        'Levenshtein~=0.25.0',
        'matplotlib~=3.8.3',
        'networkx~=2.8.8',
        'nltk~=3.8.1',
        'numpy~=1.26.4',
        'pandas~=1.5.3',
        'pillow~=10.2.0',
        'plotly~=5.20.0',
        'pyyaml~=6.0.1',
        'requests~=2.31.0',
        'scikit-learn~=1.4.1',
        'scipy~=1.12.0',
        'spacy~=3.7.5',
        'statsmodels~=0.14.1',
        # See also Dockerfile for torch dependency!
        'torch~=2.2.2'
    ],
    package_data={},
    include_package_data=True
)
