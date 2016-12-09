from setuptools import setup, find_packages
import os

versionfile = open(os.path.join('Products', 'Poi', 'version.txt'))
version = versionfile.read().strip()
versionfile.close()

readmefile = open(os.path.join('Products', 'Poi', 'README.txt'))
readme = readmefile.read().strip()
readmefile.close()

historyfile = open(os.path.join('Products', 'Poi', 'HISTORY.txt'))
history = historyfile.read().strip()
historyfile.close()

long_description = readme + "\n\n" + history

setup(name='Products.Poi',
      version=version,
      description="Poi: A friendly issue tracker",
      long_description=long_description,
      # Get more strings from
      # https://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 3.2",
          "Framework :: Plone :: 3.3",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.4",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='issue tracker',
      author='Martin Aspeli',
      author_email='plone-users@lists.sourceforge.net',
      url='http://plone.org/products/poi',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.AddRemoveWidget<1.5dev',
          'Products.DataGridField>=1.6b3,<1.8dev',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
