import codecs
import os
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages

# Most first-party packages of this project are plain directories without an
# __init__.py (compass_metrics_v2, compass_model/collaboration/...,
# compass_model_v2/...), so find_packages() drops them from the distribution
# while packaged modules keep importing them.
PACKAGES = [
    "compass_common",
    "compass_contributor",
    "compass_metrics",
    "compass_metrics_model",
    "compass_metrics_v2",
    "compass_model",
    "compass_model_v2",
    "compass_prediction",
]


setup(name="compass_metrics_model",
      description="Metrics Model",
      url="https://github.com/open-metrics-code/compass-metrics-model",
      version="0.1.0",
      author="Chenqi Shan, Yehui Wang",
      author_email="chenqishan337@gmail.com",
      license="GPLv3",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'],
      keywords="Metric Model",
      packages=find_namespace_packages(include=[package + "*" for package in PACKAGES]),
      package_data={
          'compass_metrics_model': ['resources/*'],
          'compass_metrics': ['resources/*'],
          'compass_contributor': ['conf_utils/*']
      },
      python_requires='>=3.4',
      setup_requires=['wheel'],
      zip_safe=False
      )
