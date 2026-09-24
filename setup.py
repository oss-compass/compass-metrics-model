import codecs
import os
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages


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
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11'],
      keywords="Metric Model",
      packages=find_packages(),
      package_data={
          'compass_metrics_model': ['resources/*'],
          'compass_metrics': ['resources/*'],
          'compass_contributor': ['conf_utils/*']
      },
      # grimoirelab-elk, which compass_metrics_model imports for the
      # ElasticSearch helpers and the enriched utils, declares
      # "requires-python >= 3.8".  Announcing the same requirement here
      # makes pip refuse the install on an older interpreter instead of
      # failing later with a confusing gcc error while grimoirelab-elk is
      # built from source.
      python_requires='>=3.8',
      setup_requires=['wheel'],
      zip_safe=False
      )
