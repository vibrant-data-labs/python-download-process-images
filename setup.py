# To update the pypi package:
# You need an account at pypi.org and to be added to the project
#
# increment version
# remove egg info, dist
# python setup.py sdist
# python setup.py bdist_wheel --universal
# twine upload dist/*
#
# Local, editable install:
# pip install -e ~/Github/python-download-process-images
#

from setuptools import setup
from setuptools import find_packages

setup(name='python_download_process_images',
      version='0.0.1',
      description='python_download_process_images',
      long_description='python_download_process_images',
      url='https://github.com/vibrant-data-labs/python-download-process-images',
      author='ericberlow',
      author_email='ericberlow@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'requests',
          'requests_cache',
          'awscli',
          'boto3',
          'pandas',
          'cairosvg'
      ],
      zip_safe=False)
