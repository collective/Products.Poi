import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc

from Products.Archetypes.BaseUnit import BaseUnit
from Products.Poi.Extensions.Migrations import beta2_rc1

from StringIO import StringIO

default_user = ZopeTestCase.user_name

try:
    from Products.contentmigration.migrator import InlineFieldActionMigrator
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False

class TestBetaToRC(ptc.PoiTestCase):

    def afterSetUp(self):
        self.tracker = self.createTracker(self.folder, 'tracker', managers=(default_user,))
        self.issue = self.createIssue(self.tracker, 'an issue')
        self.response = self.createResponse(self.issue, 'a response')

    if haveContentMigrations:

        def testDataGridFieldMigration(self):
            out = StringIO()
            old = self.createTracker(self.folder, 'old-tracker')
            old.getField('availableAreas').storage.set('availableAreas', old,
                                                             ('id1 | title one | description one',
                                                              'id2 | title two | description two'))
            old.getField('availableIssueTypes').storage.set('availableIssueTypes', old,
                                                                 ('id3 | title three | description three',
                                                                  'id4 | title four | description four'))                                                
            new = self.createTracker(self.folder, 'new-tracker')
        
            beta2_rc1(self.portal, out)
            # Make sure we can migrate multiple times, too
            beta2_rc1(self.portal, out)
        
            self.assertEqual(old.getAvailableAreas(),
                            ({'id' : 'id1', 'title' : 'title one', 'description' : 'description one'},
                             {'id' : 'id2', 'title' : 'title two', 'description' : 'description two'}),
                             "(If this fails, check that contentmigration is installed - its not critical if it is not)")
            self.assertEqual(old.getAvailableIssueTypes(),
                            ({'id' : 'id3', 'title' : 'title three', 'description' : 'description three'},
                             {'id' : 'id4', 'title' : 'title four', 'description' : 'description four'}))
            self.assertEqual(new.getAvailableAreas(), 
                            ({'id' : 'ui', 'title' : 'User interface', 'description' : 'User interface issues'}, 
                             {'id' : 'functionality', 'title' : 'Functionality', 'description' : 'Issues with the basic functionality'}, 
                             {'id' : 'process', 'title' : 'Process', 'description' : 'Issues relating to the development process itself'}))
            self.assertEqual(new.getAvailableIssueTypes(), 
                            ({'id' : 'bug', 'title' : 'Bug', 'description' : 'Functionality bugs in the software'}, 
                             {'id' : 'feature', 'title' : 'Feature', 'description' : 'Suggested features'}, 
                             {'id' : 'patch', 'title' : 'Patch', 'description' : 'Patches to the software'}))


        def testIssueStateChangeMigration(self):
            self.setRoles(['Manager'])
            self.portal.portal_workflow.doActionFor(self.issue, 'accept-unconfirmed')
            self.response._issueStateBefore = 'unconfirmed'
            self.response._issueStateAfter = 'open'
        
            out = StringIO()
            beta2_rc1(self.portal, out)
            # Make sure we can migrate multiple times, too
            beta2_rc1(self.portal, out)
        
            self.failIf(hasattr(self.response, '_issueStateBefore'))
            self.failIf(hasattr(self.response, '_issueStateAfter'))
            changes = self.response.getIssueChanges()
            self.assertEqual(len(changes), 1)
            self.assertEqual(changes[0], {'id' : 'review_state', 'name' : 'Issue state', 'before' : 'unconfirmed', 'after' : 'open'})


        def testIssueOverviewAndDetailsMigration(self):
            self.issue.description = BaseUnit('description', file='Description', instance=self.issue, mimetype='text/plain')
            self.issue.setDetails('<p>Foo <b>bar</b></p>', mimetype='text/html')
            
            out = StringIO()
            beta2_rc1(self.portal, out)
            # Make sure we can migrate multiple times, too
            beta2_rc1(self.portal, out)
            
            self.assertEqual(self.issue.getRawDetails(), 'Description\n\nFoo bar\n\n')
            
        def testResponseTextMigration(self):
            self.response.setResponse('<p>Foo <b>bar</b></p>', mimetype = 'text/html')
            
            out = StringIO()
            beta2_rc1(self.portal, out)
            # Make sure we can migrate multiple times, too
            beta2_rc1(self.portal, out)
            
            self.assertEqual(self.response.getRawResponse(), 'Foo bar\n\n')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBetaToRC))
    return suite

if __name__ == '__main__':
    framework()
