# -*- coding: utf-8 -*-
from Testing import ZopeTestCase

from Products.Poi.config import DESCRIPTION_LENGTH
from Products.Poi.tests import ptc

default_user = ZopeTestCase.user_name


class TestIssue(ptc.PoiTestCase):
    """Test issue functionality"""

    def afterSetUp(self):
        self.addMember('member1', 'Member One', 'member1@example.com',
                       ['Member'], '2005-01-01')
        self.addMember('member2', 'Member Two', 'member2@example.com',
                       ['Member'], '2005-01-01')
        self.addMember('member3', 'Member Three', 'member3@example.com',
                       ['Member'], '2005-01-01')
        self.tracker = self.createTracker(
            self.folder, 'issue-tracker', managers=('member1', 'member2'))
        self.issue = self.createIssue(self.tracker)

    def testEditIssue(self):
        self.issue.setTitle('title')
        self.issue.setRelease('2.0')
        self.issue.setArea('functionality')
        self.issue.setIssueType('feature')
        self.issue.setSeverity('Critical')
        self.issue.setTargetRelease('2.0')
        self.issue.setDetails('details', mimetype='text/x-web-intelligent')
        self.issue.setSteps('step1\nstep2', mimetype='text/x-web-intelligent')
        # self.issue.setAttachment(None)
        self.issue.setContactEmail('member1@example.com')
        self.issue.setWatchers(('member1', 'member2'), )
        self.issue.setResponsibleManager('member2')

        self.assertEqual(self.issue.Title(), 'title')
        self.assertEqual(self.issue.getRelease(), '2.0')
        self.assertEqual(self.issue.getArea(), 'functionality')
        self.assertEqual(self.issue.getIssueType(), 'feature')
        self.assertEqual(self.issue.getSeverity(), 'Critical')
        self.assertEqual(self.issue.getTargetRelease(), '2.0')
        self.assertEqual(self.issue.getDetails(), 'details')
        self.assertEqual(self.issue.getSteps(), 'step1<br />step2')
        # self.assertEqual(self.issue.getAttachment(), None)
        self.assertEqual(self.issue.getContactEmail(), 'member1@example.com')
        self.assertEqual(self.issue.getWatchers(), ('member1', 'member2'))
        self.assertEqual(self.issue.getWatchers(), ('member1', 'member2'))
        self.assertEqual(self.issue.getResponsibleManager(), 'member2')

    def testIsValid(self):
        self.failUnless(self.issue.isValid())

    def testRenameAfterCreation(self):
        self.failUnless(self.issue.getId() == '1')
        self.createIssue(self.tracker)
        self.failUnless(len(self.tracker.objectIds()) == 2)
        self.failUnless('1' in self.tracker.objectIds())
        self.failUnless('2' in self.tracker.objectIds())

    def testSearchableText(self):
        self.failIf('Response-text' in self.issue.SearchableText())
        self.createResponse(self.issue, text='Response-text')
        self.failUnless('Response-text' in self.issue.SearchableText())

    def testManagersVocabContainsUnassigned(self):
        vocab = self.issue.getManagersVocab()
        self.failUnless('(UNASSIGNED)' in vocab)

    def testReleasesVocabContainsUnassigned(self):
        vocab = self.issue.getManagersVocab()
        self.failUnless('(UNASSIGNED)' in vocab)

    def testValidateWatchers(self):
        self.failUnless(self.issue.validate_watchers(('member1', )) is None)
        self.failIf(self.issue.validate_watchers(('memberX', )) is None)
        self.failIf(self.issue.validate_watchers(('member1', 'memberX', ))
                    is None)

    def testIsWatching(self):
        self.issue.setWatchers(())
        self.failIf(self.issue.isWatching())
        self.issue.setWatchers((default_user, ))
        self.failUnless(self.issue.isWatching())

    def testToggleWatching(self):
        self.failIf(self.issue.isWatching())
        self.issue.toggleWatching()
        self.failUnless(self.issue.isWatching())

    def testTransformDetails(self):
        self.issue.setDetails('Make this a link http://test.com',
                              mimetype='text/x-web-intelligent')
        self.assertEqual(
            self.issue.getDetails(),
            'Make this a link <a href="http://test.com" rel="nofollow">'
            'http://test.com</a>')

    def testTransformSteps(self):
        self.issue.setSteps('Make this a link http://test.com',
                            mimetype='text/x-web-intelligent')
        self.assertEqual(
            self.issue.getSteps(),
            'Make this a link <a href="http://test.com" rel="nofollow">'
            'http://test.com</a>')

    def testExplicitDescription(self):
        self.issue.setDescription('A description')
        self.assertEqual(self.issue.Description(), 'A description')

    def testImplicitDescription(self):
        self.issue.setDetails(
            'A short details section with a link http://test.com',
            mimetype='text/x-web-intelligent')
        self.assertEqual(
            self.issue.Description(),
            'A short details section with a link http://test.com')

    def testImplicitLongDetails(self):
        text = "The quick brown fox jumped over the lazy dog" * 20
        self.issue.setDetails(text, mimetype='text/x-web-intelligent')
        self.assertEqual(self.issue.Description(),
                         text[:DESCRIPTION_LENGTH] + '...')

    def testReadableDescription(self):
        text = ("When pasting html you can get:\r\n    - ugly line breaks,\r\n"
                "- non-breaking spaces.\r\n") * 20
        self.issue.setDetails(text, mimetype='text/x-web-intelligent')
        self.failUnless(self.issue.Description().startswith(
            "When pasting html you can get:\r\n    - ugly line breaks"))
        self.failIf("&nbsp;" in self.issue.Description())
        self.failIf("<br />" in self.issue.Description())

    def testUnicodeDescription(self):
        text = (u"The Japanese call their country Nippon or in their own "
                u"characters (I think): \xe6\x97\xa5\xe6\x9c\xac")
        self.issue.setDetails(text, mimetype='text/x-web-intelligent')
        self.failUnless(self.issue.Description() == text)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestIssue))
    return suite
