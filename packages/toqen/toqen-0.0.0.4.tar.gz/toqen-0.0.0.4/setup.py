from setuptools import setup, find_packages

# Replace with your library name and version
LIBRARY_NAME = 'toqen'
VERSION = '0.0.0.4'

setup(
  name=LIBRARY_NAME,
  version=VERSION,
  package_dir = {"": "src"},
  packages=find_packages(where='src',
                         exclude=['tests*']),  # Exclude test directories
  author='Niro',
  author_email='niro@toqen.ai',
  description='Toqen AI client distributed as a python package',
  install_requires=['requests','python-dotenv'],
)
