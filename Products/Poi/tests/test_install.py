#
# basic integration tests
#
import os, sys, traceback
from StringIO import StringIO

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneTestCase import ptc 
from Products.Poi.config import CMF_DEPENDENCIES, PROJECTNAME
from Products.Poi.Extensions.Install import install

DEPENDENCIES = CMF_DEPENDENCIES

[ ZopeTestCase.installProduct(x) for x in CMF_DEPENDENCIES + [PROJECTNAME]  ]

portal_id = 'p2'

ptc.setupPloneSite(id=portal_id)

class TestPloneInstall(ptc.PloneTestCase):
    """ basic test for installation, qi """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        
    def getPortal(self):
        """ overides setup method to use our new portal """
        return self.app[portal_id]

    def installProducts(self, products):
        """ install a list of products using the quick installer """
        if type(products)!=type([]):
            products = [products,]
            
        self.portal.portal_quickinstaller.installProducts(products, stoponerror=1)

    def testQIDependencies(self):
        try:
            self.installProducts(DEPENDENCIES) 
        except :
            self.fail_tb('QI install failed')

    def testQuickInstall(self):
        try:
            self.installProducts([PROJECTNAME])
        except :
            self.fail_tb('QI install failed')
            
    def testInstallMethod(self):
        try:
            install(self.portal)
        except:
            self.fail_tb('Install from method failed')

    def fail_tb(self, msg):
        """ special fail for capturing errors::good for integration testing(qi, etc) """
        out = StringIO()
        t, e, tb = sys.exc_info()
        traceback.print_exc(tb, out)
        self.fail("%s ::\n %s\n %s\n %s\n" %( msg, t, e,  out.getvalue()) )

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneInstall))
    return suite

if __name__ == '__main__':
    framework()
