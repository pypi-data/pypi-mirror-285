from setuptools import setup, find_packages

def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
        changelog_content = f.read()
    return f"{readme_content}\n\n{changelog_content}"

setup(
  name='cropwiseworker',
  version='0.0.6',
  author='Molev Arkhip',
  author_email='jobarkhip@gmail.com',
  description='The module implements functions for working with the API of the Cropwise Operations digital management platform.',
  long_description=readme(),

  url='https://github.com/molevaa/cropwiseworker',
  download_url='https://github.com/molevaa/cropwiseworker/archive/refs/heads/main.zip',

  
  long_description_content_type='text/markdown',
  packages=['cropwiseworker'],
  install_requires=['requests','pandas','shapely','simplekml'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent'
  ],
  keywords='cropwise',
  python_requires='>=3.7'
)
