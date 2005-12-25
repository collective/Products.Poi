import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Poi.tests import ptc

default_user = ZopeTestCase.user_name

class TestTransforms(ptc.PoiTestCase):
    """Test registered portal_transforms"""

    def afterSetUp(self):
        self.transforms = self.portal.portal_transforms

    def performTransform(self, orig, transforms, mimetype = 'text/plain'):
        kwargs = {'context' : self.portal, }
        data = self.transforms._wrap(mimetype)
        for transformName in transforms:
            transform = self.transforms[transformName]
            data = transform.convert(orig, data, **kwargs)
            orig = data.getData()
            self.transforms._setMetaData(data, transform)
        return orig

    def testHyperlinks(self):
        orig = "A test http://test.com"
        new = self.performTransform(orig, ('intelligent_plain_text',))
        self.assertEqual(new, 'A test <a href="http://test.com">http://test.com</a>')

    def testMailto(self):
        orig = "A test test@test.com of mailto"
        new = self.performTransform(orig, ('intelligent_plain_text',))
        self.assertEqual(new, 'A test <a href="mailto:test@test.com">test@test.com</a> of mailto')
    
    def testTextAndLinks(self):
        orig = """A test
URL: http://test.com End
Mail: test@test.com End
URL: http://foo.com End
"""
        new = self.performTransform(orig, ('text_to_html', 'intelligent_plain_text',))
        self.assertEqual(new, '<p>A test<br />' \
                              'URL: <a href="http://test.com">http://test.com</a> End<br />' \
                              'Mail: <a href="mailto:test@test.com">test@test.com</a> End<br />' \
                              'URL: <a href="http://foo.com">http://foo.com</a> End</p>')
                              
    def testTextAndLinksAtEndOfLine(self):
        orig = """A test
URL: http://test.com
Mail: test@test.com
URL: http://foo.com
"""
        new = self.performTransform(orig, ('text_to_html', 'intelligent_plain_text',))
        self.assertEqual(new, '<p>A test<br />' \
                              'URL: <a href="http://test.com">http://test.com</a><br />' \
                              'Mail: <a href="mailto:test@test.com">test@test.com</a><br />' \
                              'URL: <a href="http://foo.com">http://foo.com</a></p>')
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTransforms))
    return suite

if __name__ == '__main__':
    framework()
