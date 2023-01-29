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
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'],
      keywords="Metric Model",
      packages=find_packages(),
      python_requires='>=3.4',
      setup_requires=['wheel'],
      zip_safe=False
      )
