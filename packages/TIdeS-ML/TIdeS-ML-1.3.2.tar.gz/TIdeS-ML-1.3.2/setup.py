from setuptools import setup
from setuptools import find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   python_requires = ">=3.8.0" and "<= 3.11.7",
   name='TIdeS-ML',
   version='1.3.2',
   description='Tool for ORF-calling and ORF-classification using ML approaches',
   license="MIT",
   long_description = long_description,
   long_description_content_type='text/markdown',
   author='Xyrus X. Maurer-Alcala',
   author_email='xmaurer-alcala@amnh.org',
   url="https://github.com/xxmalcala/TIdeS",
   # package_dir = {'':'tides'},
   packages = ['tides','tides/bin'],
   # packages = find_packages('tides'),
   install_requires=['biopython==1.79', 'ete3>=3.1.2', 'optuna>=3.1.1', 'pandas==2.1.1', 'seaborn>=0.12.2', 'scikit-learn>=1.5.0'],
   entry_points = {
        'console_scripts': ['tides = tides.tides:main'],
    },
   classifiers=[
       "Intended Audience :: Science/Research",
       "Intended Audience :: Developers",
       "Intended Audience :: Science/Research",
       "License :: Freely Distributable",
       "Development Status :: 5 - Production/Stable",
       "Operating System :: OS Independent",
       "Programming Language :: Python",
       "Programming Language :: Python :: 3",
       "Programming Language :: Python :: 3.8",
       "Programming Language :: Python :: 3.9",
       "Programming Language :: Python :: 3.10",
       "Programming Language :: Python :: 3.11",
       "Topic :: Scientific/Engineering",
       "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
)
