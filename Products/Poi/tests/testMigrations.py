import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc

from Products.Poi.Extensions.Migrations import beta2_rc1

from StringIO import StringIO

class TestMigrations(ptc.PoiTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.old = self.createTracker(self.folder, 'old-tracker')
        self.old.getField('availableAreas').storage.set('availableAreas', self.old,
                                                         ('id1 | title one | description one',
                                                          'id2 | title two | description two'))
        self.old.getField('availableIssueTypes').storage.set('availableIssueTypes', self.old,
                                                             ('id3 | title three | description three',
                                                              'id4 | title four | description four'))
        self.new = self.createTracker(self.folder, 'new-tracker')

    def testBeta2ToRc1(self):
        out = StringIO()
        beta2_rc1(self.portal, out)
        self.assertEqual(self.old.getAvailableAreas(),
                        ({'id' : 'id1', 'title' : 'title one', 'description' : 'description one'},
                         {'id' : 'id2', 'title' : 'title two', 'description' : 'description two'}),
                         "(If this fails, check that contentmigration is installed - its not critical if it is not)")
        self.assertEqual(self.old.getAvailableIssueTypes(),
                        ({'id' : 'id3', 'title' : 'title three', 'description' : 'description three'},
                         {'id' : 'id4', 'title' : 'title four', 'description' : 'description four'}))
        self.assertEqual(self.new.getAvailableAreas(), 
                        ({'id' : 'ui', 'title' : 'User interface', 'description' : 'User interface issues'}, 
                         {'id' : 'functionality', 'title' : 'Functionality', 'description' : 'Issues with the basic functionality'}, 
                         {'id' : 'process', 'title' : 'Process', 'description' : 'Issues relating to the development process itself'}))
        self.assertEqual(self.new.getAvailableIssueTypes(), 
                        ({'id' : 'bug', 'title' : 'Bug', 'description' : 'Functionality bugs in the software'}, 
                         {'id' : 'feature', 'title' : 'Feature', 'description' : 'Suggested features'}, 
                         {'id' : 'patch', 'title' : 'Patch', 'description' : 'Patches to the software'}))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations))
    return suite

if __name__ == '__main__':
    framework()
