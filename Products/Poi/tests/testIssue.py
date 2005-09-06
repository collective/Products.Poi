#
# Skeleton ContextHelpTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc

default_user = ZopeTestCase.user_name

class TestIssue(ptc.PoiTestCase):
    """Test issue functionality"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@member.com', ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@member.com', ['Member'], '2005-01-01')
        self.addMember('member3', 'Member Three', 'member3@member.com', ['Member'], '2005-01-01')
        self.tracker = self.createTracker(self.folder, 'issue-tracker', managers=('member1', 'member2'))
        self.issue = self.createIssue(self.tracker)

    def testEditIssue(self):
        self.issue.setTitle('title')
        self.issue.setDescription('overview')
        self.issue.setRelease('2.0')
        self.issue.setArea('functionality')
        self.issue.setIssueType('feature')
        self.issue.setSeverity('Critical')
        self.issue.setDetails('<p>details</p>')
        self.issue.setSteps(('step1', 'step2'))
        # self.issue.setAttachment(None)
        self.issue.setContactEmail('member1@member.com')
        self.issue.setWatchers(('member1', 'member2'),)
        self.issue.setResponsibleManager('member2')
        
        self.assertEqual(self.issue.Title(), 'title')
        self.assertEqual(self.issue.Description(), 'overview')
        self.assertEqual(self.issue.getRelease(), '2.0')
        self.assertEqual(self.issue.getArea(), 'functionality')
        self.assertEqual(self.issue.getIssueType(), 'feature')
        self.assertEqual(self.issue.getSeverity(), 'Critical')
        self.assertEqual(self.issue.getDetails(), '<p>details</p>')
        self.assertEqual(self.issue.getSteps(), ('step1', 'step2'))
        # self.assertEqual(self.issue.getAttachment(), None)
        self.assertEqual(self.issue.getContactEmail(), 'member1@member.com')
        self.assertEqual(self.issue.getWatchers(), ('member1', 'member2',))
        self.assertEqual(self.issue.getWatchers(), ('member1', 'member2',))
        self.assertEqual(self.issue.getResponsibleManager(), 'member2')

    def testIsValid(self):
        self.failUnless(self.issue.isValid())
        self.issue.setContactEmail('')
        self.failIf(self.issue.isValid())

    def testRenameAfterCreation(self):
        self.failUnless(self.issue.getId() == '1')
        self.createIssue(self.tracker)
        self.failUnless(len(self.tracker.objectIds()) == 2)
        self.failUnless('1' in self.tracker.objectIds())
        self.failUnless('2' in self.tracker.objectIds())

    def testSearchableText(self):
        self.failIf('Response-text' in self.issue.SearchableText())
        self.createResponse(self.issue, text='Response-text')
        self.issue.updateResponses()
        self.failUnless('Response-text' in self.issue.SearchableText())

    def testManagersVocabContainsUnassigned(self):
        vocab = self.issue.getManagersVocab()
        self.failUnless('(UNASSIGNED)' in vocab)

    def testReleasesVocabContainsUnassigned(self):
        vocab = self.issue.getManagersVocab()
        self.failUnless('(UNASSIGNED)' in vocab)

    def testValidateWatchers(self):
        self.failUnless(self.issue.validate_watchers(('member1',)) is None)
        self.failIf(self.issue.validate_watchers(('memberX',)) is None)
        self.failIf(self.issue.validate_watchers(('member1','memberX',)) is None)
    
    def testIsWatching(self):
        self.issue.setWatchers(())
        self.failIf(self.issue.isWatching())
        self.issue.setWatchers((default_user,))
        self.failUnless(self.issue.isWatching())
    
    def testToggleWatching(self):
        self.failIf(self.issue.isWatching())
        self.issue.toggleWatching()
        self.failUnless(self.issue.isWatching())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIssue))
    return suite

if __name__ == '__main__':
    framework()
