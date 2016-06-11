# -*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

"""
打包的用的setup必须引入，
"""

VERSION = '0.3.0'

setup(name='danmu.fm',
      version=VERSION,
      package_data={'danmufm': ['template/*', ]},
      description="a tiny and smart cli player of douyu based on Python",
      long_description='just enjoy',
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python douyu danmu danmu.fm terminal',
      author='twocucao',
      author_email='twocucao@gmail.com',
      url='https://github.com/twocucao/doumu.fm',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'requests',
      ],
      entry_points={
          'console_scripts': [
              'danmu.fm = danmufm.danmu:main'
          ]
      },
      )

# install_requires=[
# 'requests',
# 'pycookiecheat'
# ] + (['pyobjc-core', 'pyobjc'] if 'darwin' in sys.platform else []),
