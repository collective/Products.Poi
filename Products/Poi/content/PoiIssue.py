# -*- coding: utf-8 -*-
#
# File: PoiIssue.py
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

import logging
import textwrap

from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain
from Products.AddRemoveWidget.AddRemoveWidget import AddRemoveWidget
from Products.Archetypes.atapi import AttributeStorage
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import BaseObject
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import FileField
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import registerType
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFPlone.utils import getSiteEncoding
from Products.CMFPlone.utils import safe_unicode
from Products.OrderableReferenceField import OrderableReferenceField
from Products.PopupCalendarWidget.PopupCalendarWidget import PopupCalendarWidget
from collective.watcherlist.utils import get_member_email
from plone.app.blob.field import BlobField
from plone.memoize import instance
from zope.interface import implements
import transaction

from Products.Poi import PoiMessageFactory as _
from Products.Poi import permissions
from Products.Poi.adapters import IResponseContainer
from Products.Poi.config import DEFAULT_ISSUE_MIME_TYPE
from Products.Poi.config import DESCRIPTION_LENGTH
from Products.Poi.config import ISSUE_MIME_TYPES
from Products.Poi.config import PROJECTNAME
from Products.Poi.interfaces import IIssue
from Products.Poi.interfaces import ITracker
from Products.Poi.widgets import IssueReferenceWidget

wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')
logger = logging.getLogger('Poi')

PLAIN_MIMETYPES = (
    'text/x-web-intelligent',
    'text/plain',
)

schema = Schema((

    StringField(
        name='id',
        widget=StringWidget(
            visible={'view': 'invisible', 'edit': 'visible'},
            modes=('view', ),
            label=_(u'Poi_label_issue_id',
                    default=u'Id'),
        ),
        mode="r"
    ),

    StringField(
        name='title',
        widget=StringWidget(
            label=_(u"Poi_label_issue_title",
                    default=u"Title"),
            description=_(
                u'Poi_help_issue_title',
                default=(
                    u"Enter a short, descriptive title for the issue. "
                    u"A good title will make it easier for project "
                    u"managers to identify and respond to the issue.")),
        ),
        required=True,
        accessor="Title",
        searchable=True
    ),

    StringField(
        name='release',
        default="(UNASSIGNED)",
        widget=SelectionWidget(
            label=_(u'Poi_label_release',
                    default=u"Version"),
            description=_(u'Poi_help_release',
                          default=(
                              u"Select the version the issue was found in.")),
            condition="object/isUsingReleases",
        ),
        required=True,
        vocabulary='getReleasesVocab'
    ),

    TextField(
        name='details',
        allowable_content_types=ISSUE_MIME_TYPES,
        widget=RichWidget(
            label=_(u'Poi_label_details',
                    default=u"Details"),
            description=_(u'Poi_help_details',
                          default=u"Please provide further details"),
            rows=15,
            allow_file_upload=False,
        ),
        required=True,
        default_content_type=DEFAULT_ISSUE_MIME_TYPE,
        searchable=True,
        default_output_type="text/html"
    ),

    TextField(
        name='steps',
        allowable_content_types=ISSUE_MIME_TYPES,
        widget=RichWidget(
            label=_(u'Poi_label_steps',
                    default=u"Steps to reproduce"),
            description=_(
                u'Poi_help_steps',
                default=(
                    u"If applicable, please provide the steps to "
                    u"reproduce the error or identify the issue, one per "
                    u"line.")),
            rows=6,
            allow_file_upload=False,
        ),
        default_output_type="text/html",
        default_content_type=DEFAULT_ISSUE_MIME_TYPE,
        searchable=True
    ),

    BlobField(
        name='attachment',
        widget=FileWidget(
            label=_(u'Poi_label_attachment',
                    default=u"Attachment"),
            description=_(
                u'Poi_help_attachment',
                default=(
                    u"You may optionally upload a file attachment. Please "
                    u"do not upload unnecessarily large files.")),
        ),
        storage=AttributeStorage(),
        write_permission=permissions.UploadAttachment
    ),

    StringField(
        name='area',
        widget=SelectionWidget(
            label=_(u'Poi_label_area',
                    default=u"Area"),
            description=_(
                u'Poi_help_area',
                default=u"Select the area this issue is relevant to."),
        ),
        enforceVocabulary=True,
        default_method='getDefaultArea',
        vocabulary='getAreasVocab',
        required=True
    ),

    StringField(
        name='issueType',
        widget=SelectionWidget(
            label=_(u'Poi_label_issueType',
                    default=u"Issue type"),
            description=_(
                u'Poi_help_issueType',
                default=u"Select the type of issue."),
        ),
        enforceVocabulary=True,
        default_method='getDefaultIssueType',
        vocabulary='getIssueTypesVocab',
        required=True
    ),

    StringField(
        name='severity',
        widget=SelectionWidget(
            label=_(u'Poi_label_severity',
                    default=u"Severity"),
            description=_(
                u'Poi_help_severity',
                default=u"Select the severity of this issue."),
            format="radio",
        ),
        vocabulary='getAvailableSeverities',
        default_method='getDefaultSeverity',
        required=True,
        write_permission=permissions.ModifyIssueSeverity
    ),

    StringField(
        name='targetRelease',
        widget=SelectionWidget(
            label=_(u'Poi_label_targetRelease',
                    default=u"Target release"),
            description=_(
                u'Poi_help_targetRelease',
                default=u"Release this issue is targetted to be fixed in"),
            condition="object/isUsingReleases",
        ),
        vocabulary='getReleasesVocab',
        default="(UNASSIGNED)",
        required=True,
        write_permission=permissions.ModifyIssueTargetRelease
    ),

    StringField(
        name='responsibleManager',
        widget=SelectionWidget(
            label=_(u'Poi_label_responsibleManager',
                    default=u"Responsible"),
            description=_(
                u'Poi_help_responsibleManager',
                default=(
                    u"Select which manager, if any, is responsible for "
                    u"this issue.")),
        ),
        vocabulary='getManagersVocab',
        default="(UNASSIGNED)",
        required=True,
        write_permission=permissions.ModifyIssueAssignment
    ),

    StringField(
        name='contactEmail',
        validators=('isEmail', ),
        widget=StringWidget(
            label=_(u'Poi_label_contactEmail',
                    default=u"Contact email address"),
            description=_(
                u'Poi_help_contactEmail',
                default=(
                    u"Please provide an email address where you can be "
                    u"contacted for further information or when a "
                    u"resolution is available. Note that your email "
                    u"address will not be displayed to others.")),
        ),
        required=False,
        default_method='getDefaultContactEmail'
    ),

    LinesField(
        name='watchers',
        widget=LinesWidget(
            label=_(u'Poi_label_watchers',
                    default=u"Issue watchers"),
            description=_(
                u'Poi_help_watchers',
                default=(
                    u"Enter the user ids of members who are watching "
                    u"this issue, one per line. E-mail addresses are "
                    u"allowed too. These persons will "
                    u"receive an email when a response is added to the "
                    u"issue. Members can also add themselves as "
                    u"watchers.")),
        ),
        write_permission=permissions.ModifyIssueWatchers
    ),

    LinesField(
        name='subject',
        widget=AddRemoveWidget(
            label=_(u'Poi_label_subject',
                    default=u"Tags"),
            description=_(
                u'Poi_help_subject',
                default=(
                    u"Tags can be used to add arbitrary categorisation to "
                    u"issues. The list below shows existing tags which "
                    u"you can select, or you can add new ones.")),
        ),
        searchable=True,
        vocabulary='getTagsVocab',
        enforceVocabulary=False,
        write_permission=permissions.ModifyIssueTags,
        accessor="Subject"
    ),

    OrderableReferenceField('relatedIssue',
        multiValued=1,
        relationship='related_issue',
        allowed_types=('PoiIssue'),
        widget=IssueReferenceWidget(
            label=('Related issue(s)'),
            description='Link related issues')),

))

PoiIssue_schema = BaseFolderSchema.copy() + \
    schema.copy()
PoiIssue_schema.moveField('subject', after='watchers')


class PoiIssue(BaseFolder, BrowserDefaultMixin):
    """The default tracker
    """
    _at_rename_after_creation = True
    archetype_name = 'Issue'
    implements(IIssue)
    meta_type = 'PoiIssue'
    portal_type = 'PoiIssue'
    schema = PoiIssue_schema
    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'getAvailableIssueTransitions')

    def getAvailableIssueTransitions(self):
        """
        Get the available transitions for the issue.
        """
        wftool = getToolByName(self, 'portal_workflow')
        transitions = DisplayList()
        transitions.add('', 'No change')
        for tdef in wftool.getTransitionsFor(self):
            transitions.add(tdef['id'], tdef['title_or_id'])
        return transitions

    security.declareProtected(permissions.View, 'toggleWatching')

    def toggleWatching(self):
        """
        Add or remove the current authenticated member from the list of
        watchers.
        """
        portal_membership = getToolByName(self, 'portal_membership')
        if portal_membership.isAnonymousUser():
            return
        member = portal_membership.getAuthenticatedMember()
        memberId = member.getId()
        watchers = list(self.getWatchers())
        if memberId in watchers:
            watchers.remove(memberId)
        else:
            watchers.append(memberId)
        self.setWatchers(tuple(watchers))

    security.declareProtected(permissions.View, 'isWatching')

    def isWatching(self):
        """
        Determine if the current user is watching this issue or not.
        """
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member.getId() in self.getWatchers()

    security.declareProtected(permissions.View, 'getLastModificationUser')

    def getLastModificationUser(self):
        """
        Get the user id of the user who last modified the issue, either
        by creating, editing or adding a response to it. May return None if
        the user is unknown.
        """
        return getattr(self, '_lastModificationUser', None)

    # Manually created methods

    def getDefaultContactEmail(self):
        """Get the default email address, that of the creating user"""
        return get_member_email()

    def _renameAfterCreation(self, check_auto_id=False):
        parent = self.getTracker()
        maxId = 0
        for id in parent.objectIds():
            try:
                intId = int(id)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        newId = str(maxId + 1)
        # Can't rename without a subtransaction commit when using
        # portal_factory!
        transaction.savepoint(optimistic=True)
        self.setId(newId)

    def Description(self):
        """Return the explicit description or the details.

        If a description is set manually, return that.  Else returns
        the first 200 characters (defined in config.py) of the
        'details' field.

        We must avoid returning a string in one case and a unicode in
        a different case.  So we always return unicode.
        See http://plone.org/products/poi/issues/135
        """
        value = self.getField('description').get(self)
        if not value:
            value = self.getRawDetails()
            if len(value) > DESCRIPTION_LENGTH:
                value = value[:DESCRIPTION_LENGTH] + "..."
        # Always return unicode.
        if not isinstance(value, unicode):
            encoding = getSiteEncoding(self)
            value = safe_unicode(value, encoding)
        return value

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

    def getDefaultSeverity(self):
        """Get the default severity for new issues"""
        tracker = self.getTracker()
        return tracker.getDefaultSeverity()

    def getDefaultIssueType(self):
        """Get the default issue type for new issues.

        If there is only one possible issue type, we select this, else
        we select nothing.
        """
        vocab = self.getIssueTypesVocab()
        if len(vocab) == 1:
            return vocab[0]
        return None

    def getDefaultArea(self):
        """Get the default area for new issues.

        If there is only one possible area, we select this, else
        we select nothing.
        """
        vocab = self.getAreasVocab()
        if len(vocab) == 1:
            return vocab[0]
        return None

    security.declarePublic('isValid')

    def isValid(self):
        """Check if the response is valid.

        Meaning: a response has been filled in.
        """
        errors = {}
        self.Schema().validate(self, self.REQUEST, errors, 1, 1)
        if errors:
            return False
        else:
            return True

    security.declareProtected(permissions.View, 'getIssueTypesVocab')

    def getIssueTypesVocab(self):
        """
        Get the issue types available as a DisplayList.
        """
        tracker = self.getTracker()
        field = tracker.getField('availableIssueTypes')
        return field.getAsDisplayList(tracker)

    security.declareProtected(permissions.View, 'getTagsVocab')

    def getTagsVocab(self):
        """
        Get the available areas as a DispayList.
        """
        tracker = self.getTracker()
        tags = tracker.getTagsInUse()
        vocab = DisplayList()
        for t in tags:
            vocab.add(t, t)
        return vocab

    security.declareProtected(permissions.View, 'getReleasesVocab')

    def getReleasesVocab(self):
        """
        Get the vocabulary of available releases, including the item
        (UNASSIGNED) to denote that a release is not yet assigned.
        """
        vocab = DisplayList()
        vocab.add(
            '(UNASSIGNED)', _(
                u"not_assigned", default=u'(Not assigned)'))
        tracker = self.getTracker()
        trackerVocab = tracker.getReleasesVocab()
        for k in trackerVocab.keys():
            vocab.add(k, trackerVocab.getValue(k), trackerVocab.getValue(k))
        return vocab

    def SearchableText(self):
        """Include in the SearchableText the text of all responses"""
        text = BaseObject.SearchableText(self)
        folder = IResponseContainer(self, None)
        if folder is None:
            # Should Not Happen (TM)
            return text
        try:
            text += ' ' + ' '.join([r.text for r in folder if r])
        except UnicodeDecodeError:
            text = text.decode(
                'utf-8') + ' ' + ' '.join([r.text.decode('utf-8') for r in folder if r])
        return text

    def notifyModified(self):
        BaseFolder.notifyModified(self)
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        self._lastModificationUser = member.getId()

    security.declareProtected(permissions.View, 'getAreasVocab')

    def getAreasVocab(self):
        """
        Get the available areas as a DispayList.
        """
        tracker = self.getTracker()
        field = tracker.getField('availableAreas')
        return field.getAsDisplayList(tracker)

    @instance.clearbefore
    def setDetails(self, *args, **kwargs):
        self.getField('details').set(self, *args, **kwargs)

    @instance.clearbefore
    def setSteps(self, *args, **kwargs):
        self.getField('steps').set(self, *args, **kwargs)

    def _link_detect_text(self, fieldname, **kwargs):
        # perform link detection
        field = self.getField(fieldname)
        text = field.get(self, **kwargs)
        if field.getContentType(self) not in PLAIN_MIMETYPES:
            # Don't touch text/html or similar.
            return text
        tracker = self.getTracker()
        return tracker.linkDetection(text)

    @instance.memoize
    def getTaggedDetails(self, **kwargs):
        return self._link_detect_text('details', **kwargs)

    @instance.memoize
    def getTaggedSteps(self, **kwargs):
        return self._link_detect_text('steps', **kwargs)

    def getTracker(self):
        """Return the tracker.

        This gets around the problem that the aq_parent of an issue
        that is being created is not the tracker, but a temporary
        folder.
        """
        for parent in aq_chain(self):
            if ITracker.providedBy(parent):
                return parent
        raise Exception(
            "Could not find PoiTracker in acquisition chain of %r" %
            self)


registerType(PoiIssue, PROJECTNAME)
# end of class PoiIssue
