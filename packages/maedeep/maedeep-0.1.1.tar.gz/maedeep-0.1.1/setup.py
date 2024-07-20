#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 07:53:09 2021

@author: benjamin
"""

from setuptools import setup, find_packages

setup(name='maedeep',
      version='0.1.1',
        description='Python interface to use articulatory model by Maeda',
        url='https://git.ecdf.ed.ac.uk/belie/maedeep',
        author='Benjamin Elie',
        author_email='benjamin.elie@ed.ac.uk',
        license='Creative Commons Attribution 4.0 International License',
      packages=find_packages(),
      install_requires=[
        "numpy",
        "scipy",
        "tqdm",
        "shapely",
        "tensorflow", 
        "keras",
        "scikit-learn",
        "pytest"
    ],
      include_package_data=True,
      package_data={'': ['data/*.h5', 'dnn/models/*.h5',
                         'linear/models/*.h5', 'parametric/models/*.json']},
      zip_safe=False)
