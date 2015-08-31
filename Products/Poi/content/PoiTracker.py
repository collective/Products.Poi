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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.DataGridField.DataGridField import DataGridField
from Products.DataGridField.DataGridWidget import DataGridWidget
from zope.interface import implements
try:
    from Products.LinguaPlone import public as atapi
    atapi  # pyflakes
except ImportError:
    # No multilingual support
    from Products.Archetypes import atapi

from Products.Poi import PoiMessageFactory as _
from Products.Poi import permissions
from Products.Poi.config import PROJECTNAME
from Products.Poi.config import ISSUE_RECOGNITION_PATTERNS
from Products.Poi.config import REVISION_RECOGNITION_PATTERNS
from Products.Poi.interfaces import ITracker
from Products.Poi.utils import linkBugs
from Products.Poi.utils import linkSvn

schema = atapi.Schema((

    atapi.StringField(
        name='title',
        widget=atapi.StringWidget(
            label=_(u'Poi_label_tracker_title',
                    default=u"Tracker name"),
            description=_(
                u'Poi_help_tracker_title',
                default=u"Enter a descriptive name for this tracker"),
        ),
        required=True,
        accessor="Title",
        searchable=True
    ),

    atapi.TextField(
        name='description',
        widget=atapi.TextAreaWidget(
            label=_(u'Poi_label_tracker_description',
                    default=u"Tracker description"),
            description=_(
                u'Poi_help_tracker_description',
                default=u"Describe the purpose of this tracker"),
        ),
        use_portal_factory="1",
        accessor="Description",
        searchable=True,
        allowable_content_types=('text/plain'),
    ),

    atapi.TextField(
        name='helpText',
        allowable_content_types=('text/plain', 'text/structured', 'text/html',
                                 'application/msword'),
        widget=atapi.RichWidget(
            label=_(u'Poi_label_helpText',
                    default=u"Help text"),
            description=_(
                u'Poi_help_helpText',
                default=(u"Enter any introductory help text you'd like to "
                         u"display on the tracker front page.")),
        ),
        default_output_type='text/html',
        searchable=True
    ),

    DataGridField(
        name='availableAreas',
        default=({'id': 'ui',
                  'title': 'User interface',
                  'description': 'User interface issues'},
                 {'id': 'functionality',
                  'title': 'Functionality',
                  'description': 'Issues with the basic functionality'},
                 {'id': 'process',
                  'title': 'Process',
                  'description':
                  'Issues relating to the development process itself'}),
        widget=DataGridWidget(
            label=_(u'Poi_label_availableAreas',
                    default=u"Areas"),
            description=_(
                u'Poi_help_availableAreas',
                default="Enter the issue topics/areas for this tracker."),
            column_names=('Short name', 'Title', 'Description'),
        ),
        allow_empty_rows=False,
        required=True,
        columns=('id', 'title', 'description',)
    ),

    DataGridField(
        name='availableIssueTypes',
        default=({'id': 'bug',
                  'title': 'Bug',
                  'description': 'Functionality bugs in the software'},
                 {'id': 'feature',
                  'title': 'Feature',
                  'description': 'Suggested features'},
                 {'id': 'patch',
                  'title': 'Patch',
                  'description': 'Patches to the software'}),
        widget=DataGridWidget(
            label=_(u'Poi_label_availableIssueTypes',
                    default=u"Issue types"),
            description=_(u'Poi_help_availableIssueTypes',
                          default=u"Enter the issue types for this tracker."),
            column_names=('Short name', 'Title', 'Description',),
        ),
        allow_empty_rows=False,
        required=True,
        columns=('id', 'title', 'description')
    ),

    atapi.LinesField(
        name='availableSeverities',
        default=['Critical', 'Important', 'Medium', 'Low'],
        widget=atapi.LinesWidget(
            label=_(u'Poi_label_availableSeverities',
                    default=u"Available severities"),
            description=_(
                u'Poi_help_availableSeverities',
                default=(u"Enter the different type of issue severities "
                         u"that should be available, one per line.")),
        ),
        required=True
    ),

    atapi.StringField(
        name='defaultSeverity',
        default='Medium',
        widget=atapi.SelectionWidget(
            label=_(u'Poi_label_defaultSeverity',
                    default=u"Default severity"),
            description=_(
                u'Poi_help_defaultSeverity',
                default=u"Select the default severity for new issues."),
        ),
        enforceVocabulary=True,
        vocabulary='getAvailableSeverities',
        required=True
    ),

    atapi.LinesField(
        name='availableReleases',
        widget=atapi.LinesWidget(
            label=_(u'Poi_label_availableReleases',
                    default=u"Available releases"),
            description=_(
                u'Poi_help_availableReleases',
                default=(
                    u"Enter the releases which issues can be assigned to, "
                    u"one per line. If no releases are entered, issues "
                    u"will not be organised by release.")),
        ),
        required=False
    ),

    atapi.LinesField(
        name='managers',
        widget=atapi.LinesWidget(
            label=_(u'Poi_label_managers',
                    default=u"Tracker managers"),
            description=_(
                u'Poi_help_managers',
                default=(
                    u"Enter the user ids of the users who will be allowed "
                    u"to manage this tracker, one per line.")),
        ),
        default_method="getDefaultManagers"
    ),

    atapi.LinesField(
        name='technicians',
        widget=atapi.LinesWidget(
            label=_(u'Poi_label_technicians',
                    default=u"Technicians"),
            description=_(
                u'Poi_help_technicians',
                default=(
                    u"Enter the user ids of the users who will be "
                    u"responsible for solving the issues, one per line. "
                    u"Note that having only managers and no technicians "
                    u"is fine: managers can solve issues too.")),
        ),
    ),

    atapi.LinesField(
        name='watchers',
        widget=atapi.LinesWidget(
            label=_(u'Poi_label_tracker_watchers',
                    default=u"Tracker watchers"),
            description=_(
                u'Poi_help_tracker_watchers',
                default=(
                    u"Enter the user ids of members who are watching "
                    u"this tracker, one per line. E-mail addresses are "
                    u"allowed too. These persons will receive "
                    u"an email when an issue or response is added to the "
                    u"tracker. Members can also add themselves as "
                    u"watchers.")),
        ),
        write_permission=permissions.ModifyIssueWatchers
    ),

    atapi.BooleanField(
        name='sendNotificationEmails',
        default=True,
        widget=atapi.BooleanWidget(
            label=_(u'Poi_label_sendNotificationEmails',
                    default=u"Send notification emails"),
            description=_(
                u'Poi_help_sendNotificationEmails',
                default=(
                    u"If selected, tracker managers will receive an email "
                    u"each time a new issue or response is posted, and "
                    u"issue submitters will receive an email when there "
                    u"is a new response and when an issue has been "
                    u"resolved, awaiting confirmation. Technicians will "
                    u"get an email when an issue is assigned to them.")),
        ),
    ),

    atapi.StringField(
        name='mailingList',
        widget=atapi.StringWidget(
            label=_(u'Poi_label_mailingList',
                    default=u"Mailing list"),
            description=_(
                u'Poi_help_mailingList',
                default=(
                    u"If given, and if 'Send notification emails' is "
                    u"selected, an email will be sent to this address "
                    u"each time a new issue or response is posted. "
                    u"Managers will receive individual emails as well. "
                    u"If this is not wanted, you may want to make them "
                    u"technician instead.")),
        ),
        required=False,
        validators=('isEmail',)
    ),

    atapi.StringField(
        name='svnUrl',
        widget=atapi.StringWidget(
            label=_(u'Poi_label_svnurl',
                    default=u"URL to SVN"),
            description=_(
                u'Poi_help_svnurl',
                default=(
                    u"Please enter the Url to the related SVN repository, "
                    u"e.g.: "
                    u"http://dev.plone.org/changeset/%(rev)s/collective "
                    u"for products in the Plone collective.")),
            size='90',
        ),
        required=False,
    ),

))

PoiTracker_schema = atapi.BaseBTreeFolderSchema.copy() + \
    schema.copy()


class PoiTracker(atapi.BaseBTreeFolder, BrowserDefaultMixin):
    """The default tracker
    """
    _at_rename_after_creation = True
    archetype_name = 'Issue Tracker'
    implements(ITracker)
    meta_type = 'PoiTracker'
    portal_type = 'PoiTracker'
    schema = PoiTracker_schema
    security = ClassSecurityInfo()

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
        text = linkBugs(text, ids, ISSUE_RECOGNITION_PATTERNS,
                        base_url=self.absolute_url())
        svnUrl = self.getSvnUrl()
        text = linkSvn(text, svnUrl, REVISION_RECOGNITION_PATTERNS)
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
        vocab = atapi.DisplayList()
        for item in items:
            vocab.add(item, item)
        return vocab

    security.declareProtected(permissions.View, 'getTagsInUse')

    def getTagsInUse(self):
        """Get a list of the issue tags in use in this tracker."""
        catalog = getToolByName(self, 'portal_catalog')
        issues = catalog.searchResults(portal_type='PoiIssue',
                                       path='/'.join(self.getPhysicalPath()))
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

    def _updateRolesField(self, field_name, new_values):
        """Update the roles belonging to the field, and set the field value.

        For the 'managers' field: set the list of tracker managers,
        and give them the TrackerManager local role.

        For the 'techniciancs' field: set the list of technicians, and
        give them the Technician local role.

        Also clean up old roles.
        """
        if field_name == 'managers':
            role = 'TrackerManager'
        elif field_name == 'technicians':
            role = 'Technician'
        else:
            raise ValueError("Wrong tracker field name %s" % field_name)

        field = self.getField(field_name)
        current_values = field.get(self)
        field.set(self, new_values)

        to_remove = [m for m in current_values if m not in new_values]
        to_add_or_keep = new_values
        for user_id in to_remove:
            local_roles = list(self.get_local_roles_for_userid(user_id))
            if role in local_roles:
                local_roles.remove(role)
                # manage_setLocalRoles fails when called with zero roles.
                if local_roles:
                    self.manage_setLocalRoles(user_id, local_roles)
                else:
                    self.manage_delLocalRoles(to_remove)
        for user_id in to_add_or_keep:
            local_roles = list(self.get_local_roles_for_userid(user_id))
            if role not in local_roles:
                local_roles.append(role)
                self.manage_setLocalRoles(user_id, local_roles)

    def getManagersVocab(self, strict=False):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.

        Note, we now also allow Technicians here, unless we are called
        with 'strict' is True.
        """
        vocab = DisplayList()
        vocab.add(
            '(UNASSIGNED)', _(
                u"not_assigned", default=u'(Not assigned)'))
        mtool = getToolByName(self, 'portal_membership')
        for item in self.getManagers():
            user = mtool.getMemberById(item)
            if user:
                fullname = user.getProperty('fullname', item) or item
            else:
                fullname = item

            vocab.add(item, fullname)
        if not strict:
            for item in self.getTechnicians():
                user = mtool.getMemberById(item)
                if user:
                    fullname = user.getProperty('fullname', item) or item
                else:
                    fullname = item

                vocab.add(item, fullname)
            return vocab

    def getStrictManagersVocab(self):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.

        Note, this vocabulary is strictly for TrackerManagers, so not
        for Technicians.  It is not actually used by default, but can
        be handy for third parties.
        """
        return self.getManagersVocab(strict=True)

    security.declareProtected(permissions.ModifyPortalContent, 'setManagers')

    def setManagers(self, managers):
        """Set the list of tracker managers, and give them the
        TrackerManager local role.
        """
        self._updateRolesField('managers', managers)

    security.declareProtected(
        permissions.ModifyPortalContent, 'setTechnicians')

    def setTechnicians(self, technicians):
        """Set the list of technicians, and give them the
        Technician local role.
        """
        self._updateRolesField('technicians', technicians)

    security.declarePublic('getIssueWorkflowStates')

    def getIssueWorkflowStates(self):
        """Get a DisplayList of the workflow states available on issues."""
        portal_workflow = getToolByName(self, 'portal_workflow')
        chain = portal_workflow.getChainForPortalType('PoiIssue')
        workflow = getattr(portal_workflow, chain[0])
        states = getattr(workflow, 'states')
        vocab = atapi.DisplayList()
        for id, state in states.items():
            vocab.add(id, state.title)
        return vocab.sortedByValue()

    def _validate_user_ids(self, user_ids):
        """Make sure the user ids are actual user ids"""
        membership = getToolByName(self, 'portal_membership')
        not_found = []
        for user_id in user_ids:
            member = membership.getMemberById(user_id)
            if member is None:
                not_found.append(user_id)
        if not_found:
            return "The following user ids could not be found: %s" % \
                ','.join(not_found)

    def validate_managers(self, value):
        """Make sure issue tracker managers are actual user ids"""
        return self._validate_user_ids(value)

    def validate_technicians(self, value):
        """Make sure issue technicians are actual user ids"""
        return self._validate_user_ids(value)

    def validate_watchers(self, value):
        """Make sure watchers are actual user ids or email addresses."""
        membership = getToolByName(self, 'portal_membership')
        plone_utils = getToolByName(self, 'plone_utils')
        notFound = []
        for userId in value:
            member = membership.getMemberById(userId)
            if member is None:
                # Maybe an email address
                if not plone_utils.validateSingleEmailAddress(userId):
                    notFound.append(userId)
        if notFound:
            return "The following user ids could not be found: %s" % \
                ','.join(notFound)
        return None

    def getDefaultManagers(self):
        """The default list of managers should include the tracker owner"""
        return (self.Creator(), )


atapi.registerType(PoiTracker, PROJECTNAME)
