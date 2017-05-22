from Acquisition import aq_base
from DateTime import DateTime
from plone import api
from plone.app.textfield import RichTextValue
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.MailHost.interfaces import IMailHost
from Testing import ZopeTestCase
from zope.component import getSiteManager
from zope.component import getUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectModifiedEvent

from Products.Poi.adapters import IResponseContainer
from Products.Poi.content.issue import next_issue_id


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

ZopeTestCase.installProduct('Poi')

from Products.PloneTestCase import PloneTestCase
from Products.CMFPlone.tests.utils import MockMailHost
PloneTestCase.setupPloneSite(products=['Poi'])


def rich_text(original):
    return RichTextValue(original, 'text/plain', 'text/html')


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
        # Make sure our mock mailhost does not give a mailhost_warning
        # in the overview-controlpanel.
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(
            IMailSchema, prefix='plone', check=False)
        mail_settings.smtp_host = u'mock'
        mail_settings.email_from_address = 'admin@example.com'

        # Setup session (not sure why)
        self.app.REQUEST['SESSION'] = self.Session()

    def _clear(self, call_close_hook=0):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)
        PloneTestCase.PloneTestCase._clear(self)

    def addMember(self, username, fullname, email, roles, last_login_time):
        # Taken from CMFPlone/tests/testMemberDataTool
        self.portal.portal_membership.addMember(username, 'secret', roles, [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties(
            {'fullname': fullname, 'email': email,
             'last_login_time': DateTime(last_login_time)})

    def createTracker(
            self, folder, id, title=u'', description=u'', helpText=u'',
            availableAreas=[
                {'short_name': u'ui', 'title': u'User interface',
                 'description': u'User interface issues'},
                {'short_name': u'functionality', 'title': u'Functionality',
                 'description': u'Issues with the basic functionality'},
                {'short_name': u'process', 'title': u'Process',
                 'description':
                 u'Issues relating to the development process itself'},
            ],
            availableIssueTypes=[
                {'short_name': u'bug', 'title': u'Bug',
                 'description': u'Functionality bugs in the software'},
                {'short_name': u'feature', 'title': u'Feature',
                 'description': u'Suggested features'},
                {'short_name': u'patch', 'title': u'Patch',
                 'description': u'Patches to the software'},
            ],
            availableSeverities=[u'Critical', u'Important', u'Medium', u'Low'],
            defaultSeverity=u'Medium',
            availableReleases=[u'2.0', u'1.0'],
            assignees=[],
            sendNotificationEmails=False,
            mailingList=u'list@example.com'):
        """Create a new tracker in the given folder"""
        self.setRoles(['Manager'])
        folder.invokeFactory('Tracker', id)
        tracker = getattr(folder, id)
        tracker.title = title
        tracker.description = description
        tracker.help_text = helpText
        tracker.available_areas = availableAreas
        tracker.available_issue_types = availableIssueTypes
        tracker.available_severities = availableSeverities
        tracker.default_severity = defaultSeverity
        tracker.available_releases = availableReleases
        tracker.assignees = assignees
        tracker.notification_emails = sendNotificationEmails
        tracker.mailing_list = mailingList
        tracker.reindexObject()
        notify(ObjectAddedEvent(tracker))
        self.setRoles(['Member'])

        return tracker

    def createIssue(self, tracker, title=u'An issue',
                    details=u'Something is wrong', release=u'1.0',
                    area=u'ui', issueType=u'bug', severity=u'Medium',
                    targetRelease=u'2.0',
                    steps=u'', attachment=None,
                    contactEmail='submitter@example.com',
                    watchers=[],
                    tags=[],
                    assignee=None):
        """Create an issue in the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        issue_id = next_issue_id(tracker)
        issue = api.content.create(
            id=issue_id,
            container=tracker,
            type='Issue',
            title=title,
            release=release,
            area=area,
            issue_type=issueType,
            severity=severity,
            target_release=targetRelease,
            details=rich_text(details),
            steps=rich_text(steps),
            attachment=attachment,
            watchers=watchers,
            contact_email=contactEmail,
            subject=tags,
            assignee=assignee,
        )
        issue.reindexObject()
        notify(ObjectAddedEvent(issue))
        return issue

    def createResponse(self, issue, text='Response text', issueTransition='',
                       newSeverity=None, newTargetRelease=None,
                       newAssignee=None, attachment=None):
        """Create a response to the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        from Products.Poi.browser.response import Create
        request = issue.REQUEST
        # disable CSRF protection during tests
        alsoProvides(request, IDisableCSRFProtection)
        request.form['response'] = text
        request.form['transition'] = issueTransition
        if newSeverity is not None:
            request.form['severity'] = newSeverity
        if newTargetRelease is not None:
            request.form['targetRelease'] = newTargetRelease
        if newAssignee is not None:
            request.form['assignee'] = newAssignee
        if attachment is not None:
            request.form['attachment'] = attachment
        create_view = Create(issue, request)
        # A response is created by calling this view:
        create_view()

        container = IResponseContainer(issue)
        id = str(len(container) - 1)
        response = container[id]

        # In tests we need to fire this event manually:
        notify(ObjectModifiedEvent(response))
        return response


class PoiFunctionalTestCase(PoiTestCase, PloneTestCase.FunctionalTestCase):
    pass
