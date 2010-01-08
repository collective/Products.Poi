from Acquisition import aq_base
from Testing import ZopeTestCase
from DateTime import DateTime
from zope.event import notify
from zope.component import getSiteManager
from zope.lifecycleevent import ObjectModifiedEvent
from Products.Archetypes.event import ObjectInitializedEvent
from Products.MailHost.interfaces import IMailHost

from Products.Poi.adapters import IResponseContainer


# Make the boring stuff load quietly
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
ZopeTestCase.installProduct('CMFHelpIcons', quiet=1)
ZopeTestCase.installProduct('CMFQuickInstallerTool', quiet=1)
ZopeTestCase.installProduct('CMFFormController', quiet=1)
ZopeTestCase.installProduct('GroupUserFolder', quiet=1)
ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
ZopeTestCase.installProduct('TextIndexNG2', quiet=1)
ZopeTestCase.installProduct('SecureMailHost', quiet=1)
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('DataGridField')
ZopeTestCase.installProduct('AddRemoveWidget')

ZopeTestCase.installProduct('Poi')

from Products.PloneTestCase import PloneTestCase
#from Products.CMFPlone.tests.test_mails import MockMailHostTestCase
from Products.CMFPlone.tests.utils import MockMailHost
PloneTestCase.setupPloneSite(products=['Poi'])


class PoiTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):

        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        # Replace normal mailhost with mock mailhost
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        # Setup session (not sure why)
        self.app.REQUEST['SESSION'] = self.Session()

    def _clear(self, call_close_hook=0):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)
        PloneTestCase.PloneTestCase._clear(self)

    def addMember(self, username, fullname, email, roles, last_login_time):
        # Taken from CMFPlone/tests/testMemberDataTool
        self.portal.portal_membership.addMember(username, 'secret', roles, [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties(
            {'fullname': fullname, 'email': email,
             'last_login_time': DateTime(last_login_time)})

    def createTracker(self, folder, id, title='', description='', helpText='',
                        availableAreas=({'id': 'ui', 'title': 'User interface', 'description': 'User interface issues'}, {'id': 'functionality', 'title': 'Functionality', 'description': 'Issues with the basic functionality'}, {'id': 'process', 'title': 'Process', 'description': 'Issues relating to the development process itself'}),
                        availableIssueTypes=({'id': 'bug', 'title': 'Bug', 'description': 'Functionality bugs in the software'}, {'id': 'feature', 'title': 'Feature', 'description': 'Suggested features'}, {'id': 'patch', 'title': 'Patch', 'description': 'Patches to the software'}),
                        availableSeverities=['Critical', 'Important', 'Medium', 'Low'],
                        defaultSeverity='Medium',
                        availableReleases=['2.0', '1.0'],
                        managers=[],
                        sendNotificationEmails=False,
                        mailingList=''):
        """Create a new tracker in the given folder"""
        self.setRoles(['Manager'])
        folder.invokeFactory('PoiTracker', id)
        tracker = getattr(folder, id)
        tracker.setTitle(title)
        tracker.setDescription(description)
        tracker.setHelpText(helpText)
        tracker.setAvailableAreas(availableAreas)
        tracker.setAvailableIssueTypes(availableIssueTypes)
        tracker.setAvailableSeverities(availableSeverities)
        tracker.setDefaultSeverity(defaultSeverity)
        tracker.setAvailableReleases(availableReleases)
        tracker.setManagers(managers)
        tracker.setSendNotificationEmails(sendNotificationEmails)
        tracker.setMailingList(mailingList)
        tracker.reindexObject()
        self.setRoles(['Member'])

        return tracker

    def createIssue(self, tracker, title='An issue',
                    details='Something is wrong', release='(UNASSIGNED)',
                    area='ui', issueType='bug', severity='Medium',
                    targetRelease='(UNASSIGNED)',
                    steps='', attachment=None,
                    contactEmail='submitter@domain.com',
                    watchers=(),
                    tags=(),
                    responsibleManager='(UNASSIGNED)'):
        """Create an issue in the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        newId = self.portal.generateUniqueId('PoiIssue')
        oldIds = tracker.objectIds()
        tracker.invokeFactory('PoiIssue', newId)
        issue = getattr(tracker, newId)
        issue.setTitle(title)
        issue.setRelease(release)
        issue.setArea(area)
        issue.setIssueType(issueType)
        issue.setSeverity(severity)
        issue.setTargetRelease(targetRelease)
        issue.setDetails(details)
        issue.setSteps(steps, mimetype='text/x-web-intelligent')
        issue.setAttachment(attachment)
        issue.setContactEmail(contactEmail)
        issue.setWatchers(watchers)
        issue.setSubject(tags)
        issue.setResponsibleManager(responsibleManager)
        notify(ObjectInitializedEvent(issue))
        issue._renameAfterCreation()
        issue.reindexObject()
        return issue

    def createResponse(self, issue, text='Response text', issueTransition='',
                        newSeverity=None, newTargetRelease=None,
                        newResponsibleManager=None, attachment=None):
        """Create a response to the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        from Products.Poi.browser.response import Create
        request = issue.REQUEST
        request.form['response'] = text
        request.form['transition'] = issueTransition
        if newSeverity is not None:
            request.form['severity'] = newSeverity
        if newTargetRelease is not None:
            request.form['targetRelease'] = newTargetRelease
        if newResponsibleManager is not None:
            request.form['responsibleManager'] = newResponsibleManager
        if attachment is not None:
            request.form['attachment'] = attachment
        create_view = Create(issue, request)
        # A response is created by calling this view:
        create_view()

        container = IResponseContainer(issue)
        id = str(len(container) -1)
        response = container[id]

        # In tests we need to fire this event manually:
        notify(ObjectModifiedEvent(response))
        return response


class PoiFunctionalTestCase(PoiTestCase, PloneTestCase.FunctionalTestCase):
    pass


class PoiMigrationTestCase(PoiTestCase):

    def _setup(self):
        PoiTestCase._setup(self)
        # We run the tests as portal owner.
        self.loginAsPortalOwner()
        # Some content from other tests may still be here.  I tried
        # using layers and a separate test case but that did not help.
        # I don't get it.  At this point we can only accept the
        # situation and delete the rogue content if it is there.
        try:
            self.portal._delObject('foo')
            self.portal._delObject('bar')
        except AttributeError:
            # The content is not there after all; oh well.
            pass
        self.createOldSampleContent()

    def createOldSampleContent(self):
        from Products.Poi.content.PoiResponse import PoiResponse
        for x in ('foo', 'bar'):
            dummy = self.portal.invokeFactory('PoiTracker', x,
                                              availableReleases=['2.0', '1.0'])
            for y in ('foo', 'bar', 'baz'):
                dummy = self.portal[x].invokeFactory('PoiIssue', y)
                for z in ('foo', 'bar', 'baz', 'quux'):
                    response = PoiResponse(z)
                    dummy = self.portal[x][y]._setObject(z, response)
                    self.portal[x][y][z].reindexObject()
