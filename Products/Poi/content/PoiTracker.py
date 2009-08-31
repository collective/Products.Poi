# -*- coding: utf-8 -*-
#
# File: PoiTracker.py
#
# Copyright (c) 2006 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Martin Aspeli <optilude@gmx.net>"""
__docformat__ = 'plaintext'

from email.Utils import parseaddr, formataddr
import socket
from smtplib import SMTPException
from AccessControl import ClassSecurityInfo
try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *
from Products.Poi.interfaces.Tracker import Tracker
from Products.CMFPlone.interfaces.NonStructuralFolder import \
    INonStructuralFolder
from Products.CMFPlone.utils import safe_unicode
from Products.Poi.config import PROJECTNAME

from Products.DataGridField.DataGridField import DataGridField
from Products.Poi import permissions
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import log_exc, log
from Products.PageTemplates.GlobalTranslationService import \
    getGlobalTranslationService

from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import sets
from Products.Poi.htmlrender import renderHTML
from zope.interface import implements
from Products.Poi.interfaces import ITracker
from Products.Poi.utils import linkSvn
from Products.Poi.utils import linkBugs

schema = Schema((

    StringField(
        name='title',
        widget=StringWidget(
            label="Tracker name",
            description="Enter a descriptive name for this tracker",
            label_msgid="Poi_label_tracker_title",
            description_msgid="Poi_help_tracker_title",
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title",
        searchable=True
    ),

    TextField(
        name='description',
        widget=TextAreaWidget(
            label="Tracker description",
            description="Describe the purpose of this tracker",
            label_msgid='Poi_label_description',
            description_msgid='Poi_help_description',
            i18n_domain='Poi',
        ),
        use_portal_factory="1",
        accessor="Description",
        searchable=True
    ),

    TextField(
        name='helpText',
        allowable_content_types=('text/plain', 'text/structured', 'text/html',
                                 'application/msword'),
        widget=RichWidget(
            label="Help text",
            description="Enter any introductory help text you'd like to display on the tracker front page.",
            label_msgid='Poi_label_helpText',
            description_msgid='Poi_help_helpText',
            i18n_domain='Poi',
        ),
        default_output_type='text/html',
        searchable=True
    ),

    DataGridField(
        name='availableAreas',
        default=({'id' : 'ui', 'title' : 'User interface', 'description' : 'User interface issues'}, {'id' : 'functionality', 'title' : 'Functionality', 'description' : 'Issues with the basic functionality'}, {'id' : 'process', 'title' : 'Process', 'description' : 'Issues relating to the development process itself'}),
        widget=DataGridWidget(
            label="Areas",
            description="Enter the issue topics/areas for this tracker.",
            column_names=('Short name', 'Title', 'Description'),
            label_msgid='Poi_label_availableAreas',
            description_msgid='Poi_help_availableAreas',
            i18n_domain='Poi',
        ),
        allow_empty_rows=False,
        required=True,
        validators=('isDataGridFilled', ),
        columns=('id', 'title', 'description',)
    ),

    DataGridField(
        name='availableIssueTypes',
        default=({'id' : 'bug', 'title' : 'Bug', 'description' : 'Functionality bugs in the software'}, {'id' : 'feature', 'title' : 'Feature', 'description' : 'Suggested features'}, {'id' : 'patch', 'title' : 'Patch', 'description' : 'Patches to the software'}),
        widget=DataGridWidget(
            label="Issue types",
            description="Enter the issue types for this tracker.",
            column_names=('Short name', 'Title', 'Description',),
            label_msgid='Poi_label_availableIssueTypes',
            description_msgid='Poi_help_availableIssueTypes',
            i18n_domain='Poi',
        ),
        allow_empty_rows=False,
        required=True,
        validators=('isDataGridFilled',),
        columns=('id', 'title', 'description')
    ),

    LinesField(
        name='availableSeverities',
        default=['Critical', 'Important', 'Medium', 'Low'],
        widget=LinesWidget(
            label="Available severities",
            description="Enter the different type of issue severities that should be available, one per line.",
            label_msgid='Poi_label_availableSeverities',
            description_msgid='Poi_help_availableSeverities',
            i18n_domain='Poi',
        ),
        required=True
    ),

    StringField(
        name='defaultSeverity',
        default='Medium',
        widget=SelectionWidget(
            label="Default severity",
            description="Select the default severity for new issues.",
            label_msgid='Poi_label_defaultSeverity',
            description_msgid='Poi_help_defaultSeverity',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        vocabulary='getAvailableSeverities',
        required=True
    ),

    LinesField(
        name='availableReleases',
        widget=LinesWidget(
            label="Available releases",
            description="Enter the releases which issues can be assigned to, one per line. If no releases are entered, issues will not be organised by release.",
            label_msgid='Poi_label_availableReleases',
            description_msgid='Poi_help_availableReleases',
            i18n_domain='Poi',
        ),
        required=False
    ),

    LinesField(
        name='managers',
        widget=LinesWidget(
            label="Tracker managers",
            description="Enter the user ids of the users who will be allowed to manage this tracker, one per line.",
            label_msgid='Poi_label_managers',
            description_msgid='Poi_help_managers',
            i18n_domain='Poi',
        ),
        default_method="getDefaultManagers"
    ),

    BooleanField(
        name='sendNotificationEmails',
        default=True,
        widget=BooleanWidget(
            label="Send notification emails",
            description="If selected, tracker managers will receive an email each time a new issue or response is posted, and issue submitters will receive an email when there is a new response and when an issue has been resolved, awaiting confirmation.",
            label_msgid='Poi_label_sendNotificationEmails',
            description_msgid='Poi_help_sendNotificationEmails',
            i18n_domain='Poi',
        )
    ),

    StringField(
        name='mailingList',
        widget=StringWidget(
            label="Mailing list",
            description="""If given, and if "Send notification emails" is selected, an email will be sent to this address each time a new issue or response is posted. If no mailing list address is given, managers will receive individual emails.""",
            label_msgid='Poi_label_mailingList',
            description_msgid='Poi_help_mailingList',
            i18n_domain='Poi',
        ),
        required=False,
        validators=('isEmail',)
    ),
    StringField(
        name='svnUrl',
        widget=StringWidget(
            label="URL to SVN",
            description="""Please enter the Url to the related SVN repository, e.g.: http://dev.plone.org/collective/changeset/%(rev)s for products in the Plone collective.""",
            label_msgid='Poi_label_svnurl',
            description_msgid='Poi_help_svnurl',
            i18n_domain='Poi',
            size = '90',
        ),
        required=False,
    ),

),
)

PoiTracker_schema = BaseBTreeFolderSchema.copy() + \
    schema.copy()


class PoiTracker(BaseBTreeFolder, BrowserDefaultMixin):
    """The default tracker
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseBTreeFolder, '__implements__', ()), ) + \
        (getattr(BrowserDefaultMixin, '__implements__', ()), ) + \
        (Tracker, ) + (INonStructuralFolder, )
    implements(ITracker)

    # This name appears in the 'add' box
    archetype_name = 'Issue Tracker'

    meta_type = 'PoiTracker'
    portal_type = 'PoiTracker'
    allowed_content_types = ['PoiIssue']
    filter_content_types = 1
    global_allow = 1
    content_icon = 'PoiTracker.gif'
    immediate_view = 'base_view'
    default_view = 'poi_tracker_view'
    suppl_views = ()
    typeDescription = "An issue tracker"
    typeDescMsgId = 'description_edit_poitracker'


    actions = (


       {'action': "string:${object_url}",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': (permissions.View, ),
        'condition': 'python:1',
       },


       {'action': "string:${object_url}/edit",
        'category': "object",
        'id': 'edit',
        'name': 'Edit',
        'permissions': (permissions.ModifyPortalContent, ),
        'condition': 'python:1'
       },


    )

    _at_rename_after_creation = True

    schema = PoiTracker_schema

    # Methods

    security.declarePrivate('linkDetection')
    def linkDetection(self, text):
        """
        Detects issues and svn revision tags and creates links.
        """
        # In case we get something not string like, we just return
        # text without change
        if not isinstance(text, basestring):
            return text
        catalog = getToolByName(self, 'portal_catalog')
        issuefolder = self.restrictedTraverse('@@issuefolder')
        issues = catalog.searchResults(issuefolder.buildIssueSearchQuery(None))
        ids = frozenset([issue.id for issue in issues])

        # XXX/TODO: should these patterns live in the config file?
        text = linkBugs(text, ids,
                        ['#[1-9][0-9]*', 'issue:[1-9][0-9]*',
                         'ticket:[1-9][0-9]*', 'bug:[1-9][0-9]*'])
        svnUrl = self.getSvnUrl()
        text = linkSvn(text, svnUrl,
                       ['r[0-9]+', 'changeset:[0-9]+', '\[[0-9]+\]'])

        return text

    security.declareProtected(permissions.View, 'isUsingReleases')
    def isUsingReleases(self):
        """Return a boolean indicating whether this tracker is using releases.
        """
        return len(self.getAvailableReleases()) > 0

    security.declareProtected(permissions.View, 'getReleasesVocab')
    def getReleasesVocab(self):
        """
        Get the releases available to the tracker as a DisplayList.
        """
        items = self.getAvailableReleases()
        vocab = DisplayList()
        for item in items:
            vocab.add(item, item)
        return vocab

    security.declarePrivate('getNotificationEmailAddresses')
    def getNotificationEmailAddresses(self, issue=None):
        """
        Upon activity for the given issue, get the list of email
        addresses to which notifications should be sent. May return an
        empty list if notification is turned off. If issue is given, the
        issue poster and any watchers will also be included.
        """

        if not self.getSendNotificationEmails():
            return []

        portal_membership = getToolByName(self, 'portal_membership')

        member = portal_membership.getAuthenticatedMember()
        email = member.getProperty('email')

        # make sure no duplicates are added
        addresses = sets.Set()

        mailingList = self.getMailingList()
        if mailingList:
            addresses.add(mailingList)
        else:
            addresses.union_update([self._getMemberEmail(x, portal_membership)
                                    for x in self.getManagers() or []])

        if issue is not None:
            addresses.add(issue.getContactEmail())
            addresses.union_update([self._getMemberEmail(x, portal_membership)
                                    for x in issue.getWatchers() or []])

        addresses.discard(None)
        addresses.discard(email)

        return tuple(addresses)

    security.declarePrivate('sendNotificationEmail')
    def sendNotificationEmail(self, addresses, subject, rstText):
        """
        Send a notification email to the list of addresses

        XXX Note to self [maurits]: look at this blog post from Marius
        Gedminas, titled "Sending Unicode emails in Python":
        http://mg.pov.lt/blog/unicode-emails-in-python.html
        """

        if not self.getSendNotificationEmails() or not addresses:
            return

        portal_url  = getToolByName(self, 'portal_url')
        plone_utils = getToolByName(self, 'plone_utils')

        portal      = portal_url.getPortalObject()
        mailHost    = plone_utils.getMailHost()
        charset     = portal.getProperty('email_charset', '')
        if not charset:
            charset = plone_utils.getSiteEncoding()
        from_address = portal.getProperty('email_from_address', '')

        if not from_address:
            log('Cannot send notification email: email sender address not set')
            return
        from_name = portal.getProperty('email_from_name', '')
        mfrom = formataddr((from_name, from_address))
        if parseaddr(mfrom)[1] != from_address:
            # formataddr probably got confused by special characters.
            mfrom = from_address


        email_msg = MIMEMultipart('alternative')
        email_msg.epilogue = ''

        # Translate the body text
        ts = getGlobalTranslationService()
        rstText = ts.translate('Poi', rstText, context=self)
        # We must choose the body charset manually
        for body_charset in 'US-ASCII', charset, 'UTF-8':
            try:
                rstText = rstText.encode(body_charset)
            except UnicodeError:
                pass
            else:
                break

        textPart = MIMEText(rstText, 'plain', body_charset)
        email_msg.attach(textPart)
        htmlPart = MIMEText(renderHTML(rstText, charset=body_charset),
                            'html', body_charset)
        email_msg.attach(htmlPart)

        # Make the subject unicode and translate it too.
        subject = safe_unicode(subject, charset)
        subject = ts.translate('Poi', subject, context=self)
        for address in addresses:
            address = safe_unicode(address, charset)
            if not address:
                # E-mail address may not be known, for example in case
                # of LDAP users.  See:
                # http://plone.org/products/poi/issues/213
                continue
            try:
                # Note that charset is only used for the headers, not
                # for the body text as that is a Message/MIMEText already.
                mailHost.secureSend(message = email_msg,
                                    mto = address,
                                    mfrom = mfrom,
                                    subject = subject,
                                    charset = charset)
            except (socket.error, SMTPException), exc:
                log_exc(('Could not send email from %s to %s regarding issue '
                         'in tracker %s\ntext is:\n%s\n') % (
                        mfrom, address, self.absolute_url(), email_msg))
                log_exc("Reason: %s: %r" % (exc.__class__.__name__, str(exc)))
            except:
                raise


    security.declareProtected(permissions.View, 'getTagsInUse')
    def getTagsInUse(self):
        """Get a list of the issue tags in use in this tracker."""
        catalog = getToolByName(self, 'portal_catalog')
        issues = catalog.searchResults(portal_type = 'PoiIssue',
                                       path = '/'.join(self.getPhysicalPath()))
        tags = {}
        for i in issues:
            for s in i.Subject:
                tags[s] = 1
        keys = tags.keys()
        keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
        return keys

    security.declareProtected(permissions.View, 'getExternalTitle')
    def getExternalTitle(self):
        """ Get the external title of this tracker.

        This will be the name used in outgoing emails, for example.
        """
        return self.Title()

    # Manually created methods

    def canSelectDefaultPage(self):
        """Explicitly disallow selection of a default-page."""
        return False

    security.declareProtected(permissions.ModifyPortalContent, 'setManagers')
    def setManagers(self, managers):
        """
        Set the list of tracker managers, and give them the Manager local role.
        """
        field = self.getField('managers')
        currentManagers = field.get(self)
        field.set(self, managers)

        toRemove = [m for m in currentManagers if m not in managers]
        toAdd = [m for m in managers if m not in currentManagers]
        toKeep = [m for m in managers if m in currentManagers]
        for userId in toRemove:
            local_roles = list(self.get_local_roles_for_userid(userId))
            if 'Manager' in local_roles:
                local_roles.remove('Manager')
                if local_roles:
                    # One or more roles must be given
                    self.manage_setLocalRoles(userId, local_roles)
                else:
                    self.manage_delLocalRoles(toRemove)
        for userId in toAdd:
            local_roles = list(self.get_local_roles_for_userid(userId))
            local_roles.append('Manager')
            self.manage_setLocalRoles(userId, local_roles)
        # When creating a tracker as non-manager you used to become
        # only Owner and not Manager, which is not what we want.
        for userId in toKeep:
            local_roles = list(self.get_local_roles_for_userid(userId))
            if not 'Manager' in local_roles:
                local_roles.append('Manager')
                self.manage_setLocalRoles(userId, local_roles)

    security.declarePublic('getIssueWorkflowStates')
    def getIssueWorkflowStates(self):
        """Get a DisplayList of the workflow states available on issues."""
        portal_workflow = getToolByName(self, 'portal_workflow')
        chain = portal_workflow.getChainForPortalType('PoiIssue')
        workflow = getattr(portal_workflow, chain[0])
        states = getattr(workflow, 'states')
        vocab = DisplayList()
        for id, state in states.items():
            vocab.add(id, state.title)
        return vocab.sortedByValue()

    def validate_managers(self, value):
        """Make sure issue tracker managers are actual user ids"""
        membership = getToolByName(self, 'portal_membership')
        notFound = []
        for userId in value:
            member = membership.getMemberById(userId)
            if member is None:
                notFound.append(userId)
        if notFound:
            return "The following user ids could not be found: %s" % \
                ','.join(notFound)
        else:
            return None

    def getDefaultManagers(self):
        """The default list of managers should include the tracker owner"""
        return (self.Creator(), )

    def _getMemberEmail(self, username, portal_membership=None):
        """Query portal_membership to figure out the specified email address
        for the given user (via the username parameter) or return None if none
        is present.
        """

        if portal_membership is None:
            portal_membership = getToolByName(self, 'portal_membership')

        member = portal_membership.getMemberById(username)
        if member is None:
            return None

        try:
            email = member.getProperty('email')
        except Unauthorized:
            # this will happen if CMFMember is installed and the email
            # property is protected via AT security
            email = member.getField('email').getAccessor(member)()
        return email


def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiTracker, PROJECTNAME)
# end of class PoiTracker
