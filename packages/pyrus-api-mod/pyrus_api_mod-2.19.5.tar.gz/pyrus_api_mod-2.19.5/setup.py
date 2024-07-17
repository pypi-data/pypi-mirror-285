import os
from setuptools import setup, find_packages

setup(name="pyrus-api-mod",
      version="2.19.5",
      python_requires='>=3.4',
      description="Python Pyrus API client",
      author="tailgrabik",
      long_description=open('README.rst', 'r').read(),
      author_email="tailgrabik@gmail.com",
      url="https://pyrus.com/en/help/api",
      project_urls={
        'GitHub Project': 'https://github.com/tailgrabik/pyrusapi-python'
    },
      packages=find_packages(exclude=["*tests.*", "*test.*"]),
      license='MIT License',
      keywords="pyrus api",
      install_requires=[
          'requests',
          'jsonpickle'
      ],
      zip_safe=True)
