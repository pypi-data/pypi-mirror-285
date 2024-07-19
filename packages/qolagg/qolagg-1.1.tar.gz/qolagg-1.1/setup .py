#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from setuptools import setup, find_packages


# In[ ]:


setup(
    name = 'qolagg',
    author = 'Providence Adu,Ph.D.',
    author_email = '<padu@charlotte.edu>',
    version = '1.1',
    url='https://github.com/ProvidenceAdu/qolagg',
    description = 'This library code execute aggregate analysis for the Quality of Life Exporer variables',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    install_requires = ['pandas>=1.0.0',],
    keywords = ['urban institute','python', 'Mecklenburg County','quality of life explorer', 'aggregate','NPA']
)

