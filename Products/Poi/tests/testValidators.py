from unittest import TestSuite, makeSuite
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase


class TestValidation(ATSiteTestCase):

    def test_registration(self):
        from Products.validation import validation
        v = validation.validatorFor('isDataGridFilled')
        self.failUnlessEqual(v((0, 1)), 1)
        self.failUnlessEqual(v([0, 1]), 1)
        self.failIfEqual(v([1]), 1)
        self.failIfEqual(v(0), 1)


def test_suite():
    suite = TestSuite()

    suite.addTest(makeSuite(TestValidation))

    return suite
