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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_chain

from Products.Archetypes.atapi import AttributeStorage
from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import BaseObject
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import FileField
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import LinesField
from Products.Archetypes.atapi import LinesWidget
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextField
from Products.CMFPlone.utils import safe_unicode

from Products.Poi.config import DEFAULT_ISSUE_MIME_TYPE
from Products.Poi.config import DESCRIPTION_LENGTH
from Products.Poi.config import ISSUE_MIME_TYPES
from Products.Poi.config import PROJECTNAME
from Products.Poi.adapters import IResponseContainer

from Products.Poi import permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.AddRemoveWidget.AddRemoveWidget import AddRemoveWidget
from collective.watcherlist.utils import get_member_email

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
import transaction

import textwrap
wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')
from zope.interface import implements
from Products.Poi.interfaces import IIssue
from Products.Poi.interfaces import ITracker
from Products.Poi import PoiMessageFactory as _
from plone.memoize import instance

logger = logging.getLogger('Poi')

schema = Schema((

    StringField(
        name='id',
        widget=StringWidget(
            visible={'view': 'invisible', 'edit': 'visible'},
            modes=('view', ),
            label='Id',
            label_msgid='Poi_label_id',
            i18n_domain='Poi',
        ),
        mode="r"
    ),

    StringField(
        name='title',
        widget=StringWidget(
            label="Title",
            description=("Enter a short, descriptive title for the issue. "
                         "A good title will make it easier for project "
                         "managers to identify and respond to the issue."),
            label_msgid="Poi_label_issue_title",
            description_msgid="Poi_help_issue_title",
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title",
        searchable=True
    ),

    StringField(
        name='release',
        default="(UNASSIGNED)",
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Version",
            description="Select the version the issue was found in.",
            condition="object/isUsingReleases",
            label_msgid='Poi_label_release',
            description_msgid='Poi_help_release',
            i18n_domain='Poi',
        ),
        required=True,
        vocabulary='getReleasesVocab'
    ),

    TextField(
        name='details',
        allowable_content_types=ISSUE_MIME_TYPES,
        widget=RichWidget(
            label="Details",
            description="Please provide further details",
            rows=15,
            allow_file_upload=False,
            label_msgid='Poi_label_details',
            description_msgid='Poi_help_details',
            i18n_domain='Poi',
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
            label="Steps to reproduce",
            description=("If applicable, please provide the steps to "
                         "reproduce the error or identify the issue, one per "
                         "line."),
            rows=6,
            allow_file_upload=False,
            label_msgid='Poi_label_steps',
            description_msgid='Poi_help_steps',
            i18n_domain='Poi',
        ),
        default_output_type="text/html",
        default_content_type=DEFAULT_ISSUE_MIME_TYPE,
        searchable=True
    ),

    FileField(
        name='attachment',
        widget=FileWidget(
            label="Attachment",
            description=("You may optionally upload a file attachment. Please "
                         "do not upload unnecessarily large files."),
            label_msgid='Poi_label_attachment',
            description_msgid='Poi_help_attachment',
            i18n_domain='Poi',
        ),
        storage=AttributeStorage(),
        write_permission=permissions.UploadAttachment
    ),

    StringField(
        name='area',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Area",
            description="Select the area this issue is relevant to.",
            label_msgid='Poi_label_area',
            description_msgid='Poi_help_area',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        default_method='getDefaultArea',
        vocabulary='getAreasVocab',
        required=True
    ),

    StringField(
        name='issueType',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Issue type",
            description="Select the type of issue.",
            label_msgid='Poi_label_issueType',
            description_msgid='Poi_help_issueType',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        default_method='getDefaultIssueType',
        vocabulary='getIssueTypesVocab',
        required=True
    ),

    StringField(
        name='severity',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Severity",
            description="Select the severity of this issue.",
            format="radio",
            label_msgid='Poi_label_severity',
            description_msgid='Poi_help_severity',
            i18n_domain='Poi',
        ),
        vocabulary='getAvailableSeverities',
        default_method='getDefaultSeverity',
        required=True,
        write_permission=permissions.ModifyIssueSeverity
    ),

    StringField(
        name='targetRelease',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Target release",
            description="Release this issue is targetted to be fixed in",
            condition="object/isUsingReleases",
            label_msgid='Poi_label_targetRelease',
            description_msgid='Poi_help_targetRelease',
            i18n_domain='Poi',
        ),
        vocabulary='getReleasesVocab',
        default="(UNASSIGNED)",
        required=True,
        write_permission=permissions.ModifyIssueTargetRelease
    ),

    StringField(
        name='responsibleManager',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Responsible",
            description=("Select which manager, if any, is responsible for "
                         "this issue."),
            label_msgid='Poi_label_responsibleManager',
            description_msgid='Poi_help_responsibleManager',
            i18n_domain='Poi',
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
            label="Contact email address",
            description=("Please provide an email address where you can be "
                         "contacted for further information or when a "
                         "resolution is available. Note that your email "
                         "address will not be displayed to others."),
            label_msgid='Poi_label_contactEmail',
            description_msgid='Poi_help_contactEmail',
            i18n_domain='Poi',
        ),
        required=False,
        default_method='getDefaultContactEmail'
    ),

    LinesField(
        name='watchers',
        widget=LinesWidget(
            label="Issue watchers",
            description=("Enter the user names of members who are watching "
                         "this issue, one per line. These members will "
                         "receive an email when a response is added to the "
                         "issue. Members can also add themselves as "
                         "watchers."),
            label_msgid='Poi_label_watchers',
            description_msgid='Poi_help_watchers',
            i18n_domain='Poi',
        ),
        write_permission=permissions.ModifyIssueWatchers
    ),

    LinesField(
        name='subject',
        widget=AddRemoveWidget(
            label="Tags",
            description=("Tags can be used to add arbitrary categorisation to "
                         "issues. The list below shows existing tags which "
                         "you can select, or you can add new ones."),
            label_msgid='Poi_label_subject',
            description_msgid='Poi_help_subject',
            i18n_domain='Poi',
        ),
        searchable=True,
        vocabulary='getTagsVocab',
        enforceVocabulary=False,
        write_permission=permissions.ModifyIssueTags,
        accessor="Subject"
    ),

),
)

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

    def getManagersVocab(self, strict=False):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.

        Note, we now also allow Technicians here, unless we are called
        with 'strict' is True.
        """
        tracker = self.getTracker()
        vocab = DisplayList()
        vocab.add('(UNASSIGNED)', _(u'None'))
        for item in tracker.getManagers():
            vocab.add(item, item)
        if not strict:
            for item in tracker.getTechnicians():
                vocab.add(item, item)
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
        vocab.add('(UNASSIGNED)', _(u'None'))
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
        text += ' ' + ' '.join([r.text for r in folder if r])
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

    @instance.memoize
    def getTaggedDetails(self, **kwargs):
        # perform link detection
        text = self.getField('details').get(self, **kwargs)
        tracker = self.getTracker()
        return tracker.linkDetection(text)

    @instance.memoize
    def getTaggedSteps(self, **kwargs):
        # perform link detection
        text = self.getField('steps').get(self, **kwargs)
        tracker = self.getTracker()
        return tracker.linkDetection(text)

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
