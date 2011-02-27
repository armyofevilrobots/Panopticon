"""Panopticon"""
from setuptools import setup, find_packages

VERSION = '0.0'

setup(name='panopticon',
      version=VERSION,
      description="",
      long_description="""\
""",
      classifiers=[], #Whuzza
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      scripts=['scripts/panopticon',],
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
