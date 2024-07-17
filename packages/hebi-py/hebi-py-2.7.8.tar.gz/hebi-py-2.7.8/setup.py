# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  HEBI Core python API - Copyright 2018-2019 HEBI Robotics
#  See http://hebi.us/softwarelicense for license details
#
# -----------------------------------------------------------------------------
from os import path
from setuptools import setup, Extension, find_packages

with open('hebi/VERSION') as f:
  api_version = f.read().strip()

api_reference_url = f"https://files.hebi.us/docs/python/{api_version}/"
changelog_url = "http://docs.hebi.us/downloads_changelogs.html#python-api-changelog"
documentation_url = "http://docs.hebi.us/tools.html#python-api"
license_url = "https://www.hebirobotics.com/softwarelicense"

description = f"""
HEBI Core Python API
====================

HEBI Python provides bindings for the HEBI Core library.

API Reference available at {api_reference_url}

Documentation available on [docs.hebi.us]({documentation_url}).

Refer to the [API changelog]({changelog_url}) for version history.

By using this software, you agree to our [software license]({license_url}).
"""


setup(name='hebi-py',
      version=api_version,
      description='HEBI Core Python bindings',
      long_description=description,
      long_description_content_type="text/markdown",
      author='Chris Bollinger',
      author_email='support@hebirobotics.com',
      url='https://docs.hebi.us',
      packages=find_packages(),
      package_data={'hebi': [
          'lib/**/libhebi.so*',
          'lib/**/libhebiWrapper.so*',
          'lib/**/libhebi.*dylib',
          'lib/**/libhebiWrapper.*dylib',
          'lib/**/hebi.dll',
          'lib/**/hebiWrapper.dll',
          '_internal/*',
          '_internal/ffi/*'
      ]},
      include_package_data=True,
      install_requires=[
          'numpy>=1.24'
      ],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: MacOS X",
          "Intended Audience :: Developers",
          "Operating System :: MacOS",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: POSIX",
          "Operating System :: Unix",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: Implementation :: CPython",
      ],
      project_urls={
          "API Reference": api_reference_url,
          "Changelog": changelog_url,
          "Documentation": documentation_url,
          "Examples": "https://github.com/HebiRobotics/HEBI-python-examples"
      }
      )
