from setuptools import setup, find_packages

readmefile = open('README.rst')
readme = readmefile.read().strip()
readmefile.close()

historyfile = open('CHANGES.rst')
history = historyfile.read().strip()
historyfile.close()

long_description = readme + "\n\n" + history

setup(name='Products.Poi',
      version='4.1.0.dev0',
      description="Poi: A friendly issue tracker",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 5.2",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='bugs issue tracker',
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
          'plone.memoize',
          'plone.namedfile',
          'Products.CMFPlone>=5.2',
          'collective.dexteritytextindexer',
          'collective.watcherlist>=3.0',
          'collective.z3cform.datagridfield',
          'plone.app.relationfield>=2.0.1',
      ],
      extras_require={
          'test': [
              'Products.PloneTestCase',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
