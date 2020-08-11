from Products.Poi.tests import ptc
from Products.Poi.browser.notifications import BasePoiMail


class DummyPoiMail(BasePoiMail):
    # Override the plain '@property' with a simple property that we
    # can easily override in the tests.
    plain = u''


class TestNotifications(ptc.PoiTestCase):
    """Test email notifications

    For the moment this just checks if some plain text and html is
    being generated.
    """

    def _makeOne(self):
        # We may want to create a tracker and an issue and use the
        # issue as the context, but let's see how far we come with the
        # portal as context.
        return DummyPoiMail(self.portal, self.portal.REQUEST)

    def testCSS(self):
        # Check that the contents of the css file are being added to
        # the html by testing that at least some styling is ending up there.
        mailer = self._makeOne()
        self.assertTrue('font-size' in mailer.html)

    def testGoodRestructuredText(self):
        # Good restructured text gets interpreted:
        mailer = self._makeOne()
        mailer.plain = u"*bold* **italic**"
        self.assertTrue("<em>bold</em> <strong>italic</strong>" in mailer.html)

    def testBadRestructuredText(self):
        # Bad restructured text gets put in a 'pre' tag:
        mailer = self._makeOne()
        mailer.plain = u"This is **bad* restructured text"
        self.assertTrue("<pre>This is **bad* restructured text</pre>"
                        in mailer.html)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNotifications))
    return suite
