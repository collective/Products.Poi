from zope.testing import doctest
import unittest
from Testing.ZopeTestCase import ZopeDocFileSuite as Suite
from Products.Poi.tests.ptc import PoiMigrationTestCase

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suites = [
        Suite('migration_issue_description.txt',
              package='Products.Poi.tests',
              optionflags=OPTIONFLAGS,
              test_class=PoiMigrationTestCase),
        Suite('migration_workflow_changes.txt',
              package='Products.Poi.tests',
              optionflags=OPTIONFLAGS,
              test_class=PoiMigrationTestCase),
        Suite('migration_old_responses_original.txt',
              package='Products.Poi.tests',
              optionflags=OPTIONFLAGS,
              test_class=PoiMigrationTestCase),
        Suite('migration_old_responses_alternative.txt',
              package='Products.Poi.tests',
              optionflags=OPTIONFLAGS,
              test_class=PoiMigrationTestCase),
        Suite('upgrade_steps.txt',
              package='Products.Poi.tests',
              optionflags=OPTIONFLAGS,
              test_class=PoiMigrationTestCase),
        ]
    return unittest.TestSuite(suites)
