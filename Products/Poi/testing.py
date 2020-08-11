# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from Products.CMFPlone.tests.utils import MockMailHost
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
from zope.component import getUtility

import Products.Poi
import collective.z3cform.datagridfield


class ProductsPoiLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=Products.Poi)
        self.loadZCML(package=collective.z3cform.datagridfield)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "Products.Poi:default")

        portal._original_MailHost = portal.MailHost
        portal.MailHost = mailhost = MockMailHost("MailHost")
        sm = getSiteManager(context=portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)
        # Make sure our mock mailhost does not give a mailhost_warning
        # in the overview-controlpanel.
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone", check=False)
        mail_settings.smtp_host = u"mock"
        mail_settings.email_from_address = "admin@example.com"


PRODUCTS_POI_FIXTURE = ProductsPoiLayer()


PRODUCTS_POI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCTS_POI_FIXTURE,), name="ProductsPoiLayer:IntegrationTesting"
)


PRODUCTS_POI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCTS_POI_FIXTURE,), name="ProductsPoiLayer:FunctionalTesting"
)


PRODUCTS_POI_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(PRODUCTS_POI_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="ProductsPoiLayer:AcceptanceTesting",
)
