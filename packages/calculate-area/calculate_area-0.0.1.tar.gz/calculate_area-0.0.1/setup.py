from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='calculate_area',
  version='0.0.1',
  author='jaden',
  author_email='dmitrijkaraulov7@gmail.com',
  description='This is module for send area',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/Dmitriy1336/Area/',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='calculating area',
  project_urls={
    'GitHub': 'https://github.com/Dmitriy1336/Area/'
  },
  python_requires='>=3.6'
)