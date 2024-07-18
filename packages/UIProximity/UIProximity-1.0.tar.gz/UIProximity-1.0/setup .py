#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from setuptools import setup, find_packages


# In[ ]:


setup(
    name = 'UIProximity',
    author = 'Providence Adu,Ph.D.',
    author_email = '<padu@charlotte.edu>',
    version = '1.0',
    url='https://github.com/ProvidenceAdu/ProximityUI',
    description = 'library code execute various proximity analyses using ArcPy',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    install_requires = ['numpy>=1.18.0', 'pandas>=1.0.0',],
    keywords = ['urban institute','python', 'QOL','quality of life explorer']
)

