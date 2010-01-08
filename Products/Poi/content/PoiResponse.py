# -*- coding: utf-8 -*-
#
# File: PoiResponse.py
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

from Products.Archetypes.atapi import AttributeStorage
from Products.Archetypes.atapi import BaseContent
from Products.Archetypes.atapi import BaseSchema
from Products.Archetypes.atapi import FileField
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import SelectionWidget
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextField


from Products.Poi.config import DEFAULT_ISSUE_MIME_TYPE
from Products.Poi.config import ISSUE_MIME_TYPES
from Products.Poi.config import PROJECTNAME

from Products.Poi import permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFCore.utils import getToolByName
import transaction

import textwrap
wrapper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')
from zope.interface import implements
from Products.Poi.interfaces import IResponse
from plone.memoize import instance

schema = Schema((

    StringField(
        name='id',
        widget=StringWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
            modes=('view', ),
            label='Id',
        ),
        mode="r"
    ),

    StringField(
        name='title',
        widget=StringWidget(
            label="Subject",
            description="""Enter a brief subject for this response, e.g. "Fixed" or "Will be fixed in next release".""",
            visible={'edit': 'invisible', 'view': 'invisible'},
            modes=('view', ),
        ),
        accessor="Title",
        mode="r",
        searchable=True
    ),

    TextField(
        name='response',
        allowable_content_types=ISSUE_MIME_TYPES,
        widget=RichWidget(
            label="Response",
            description="Please enter your response below",
            rows=15,
            allow_file_upload=False,
        ),
        required=False,
        default_content_type=DEFAULT_ISSUE_MIME_TYPE,
        searchable=True,
        default_output_type="text/html"
    ),

    FileField(
        name='attachment',
        widget=FileWidget(
            label="Attachment",
            description="You may optionally upload a file attachment. Please do not upload unnecessarily large files.",
        ),
        storage=AttributeStorage(),
        write_permission=permissions.UploadAttachment
    ),

    StringField(
        name='issueTransition',
        mutator="setNewIssueState",
        widget=SelectionWidget(
            label="Change issue state",
            description="Select a change of state in the issue this response is for, if applicable",
            format="radio",
        ),
        vocabulary='getAvailableIssueTransitions',
        default='',
        enforceVocabulary=False,
        accessor="getIssueTransition",
        write_permission=permissions.ModifyIssueState
    ),

    StringField(
        name='newSeverity',
        mutator="setNewSeverity",
        widget=SelectionWidget(
            label="Change issue severity",
            description="Select the severity for this issue",
            format="radio",
        ),
        vocabulary='getAvailableSeverities',
        default_method='getCurrentIssueSeverity',
        enforceVocabulary=True,
        accessor="getNewSeverity",
        write_permission=permissions.ModifyIssueSeverity
    ),

    StringField(
        name='newTargetRelease',
        mutator="setNewTargetRelease",
        widget=SelectionWidget(
            label="Change target release",
            description="Set the target release for this issue",
            format="flex",
            condition="object/isUsingReleases",
        ),
        vocabulary='getReleasesVocab',
        default_method='getCurrentTargetRelease',
        enforceVocabulary=True,
        accessor="getNewTargetRelease",
        write_permission=permissions.ModifyIssueTargetRelease
    ),

    StringField(
        name='newResponsibleManager',
        mutator="setNewResponsibleManager",
        widget=SelectionWidget(
            label="Change responsible manager",
            description="Select the responsible manager for this issue",
            format="flex",
        ),
        vocabulary='getManagersVocab',
        default_method='getCurrentResponsibleManager',
        enforceVocabulary=True,
        accessor="getNewResponsibleManager",
        write_permission=permissions.ModifyIssueAssignment
    ),

),
)

PoiResponse_schema = BaseSchema.copy() + \
    schema.copy()


class PoiResponse(BaseContent, BrowserDefaultMixin):
    """A response to an issue, added by a project manager. When giving
    a response, the workflow state of the parent issue can be set at
    the same time.
    """
    security = ClassSecurityInfo()
    implements(IResponse)

    # This name appears in the 'add' box
    archetype_name = 'Response'

    meta_type = 'PoiResponse'
    portal_type = 'PoiResponse'
    _at_rename_after_creation = True

    schema = PoiResponse_schema

    # Methods

    security.declareProtected(permissions.ModifyIssueState, 'setNewIssueState')
    def setNewIssueState(self, transition):
        """
        Set a new review state for the parent issue, by executing
        the given transition.
        """
        # XXX: Why are we being called twice if enforceVocabulary=1 (hence)
        #  vocab becomes invalid after first time...

        if transition and transition in self.getAvailableIssueTransitions():
            wftool = getToolByName(self, 'portal_workflow')
            stateBefore = wftool.getInfoFor(self.aq_parent, 'review_state')
            wftool.doActionFor(self.aq_parent, transition)
            stateAfter = wftool.getInfoFor(self.aq_parent, 'review_state')
            self._addIssueChange('review_state', 'Issue state',
                                 stateBefore, stateAfter)

        self.getField('issueTransition').set(self, transition)

    security.declareProtected(permissions.ModifyIssueSeverity,
                              'setNewSeverity')
    def setNewSeverity(self, severity):
        """
        Set a new issue severity for the parent issue
        """
        currentIssueSeverity = self.getCurrentIssueSeverity()
        if severity and currentIssueSeverity != severity:
            self._addIssueChange('severity', 'Severity',
                                 currentIssueSeverity, severity)
            issue = self.aq_inner.aq_parent
            issue.setSeverity(severity)
            issue.reindexObject(('getSeverity', ))
        self.getField('newSeverity').set(self, severity)

    security.declareProtected(permissions.ModifyIssueTargetRelease,
                              'setNewTargetRelease')
    def setNewTargetRelease(self, release):
        """
        Set a new target release for the parent issue
        """
        currentTargetRelease = self.getCurrentTargetRelease()
        if release and currentTargetRelease != release:
            vocab = self.getReleasesVocab()
            current = vocab.getValue(currentTargetRelease)
            new = vocab.getValue(release)
            self._addIssueChange('target_release', 'Target release',
                                 current, new)
            issue = self.aq_inner.aq_parent
            issue.setTargetRelease(release)
            issue.reindexObject(('getTargetRelease', ))
        self.getField('newTargetRelease').set(self, release)

    security.declareProtected(permissions.ModifyIssueAssignment,
                              'setNewResponsibleManager')
    def setNewResponsibleManager(self, manager):
        """
        Set a new responsible manager for the parent issue
        """
        currentManager = self.getCurrentResponsibleManager()
        if manager and manager != currentManager:
            self._addIssueChange('responsible_manager', 'Responsible manager',
                                 currentManager, manager)
            issue = self.aq_inner.aq_parent
            issue.setResponsibleManager(manager)
            issue.reindexObject(('getResponsibleManager', ))
        self.getField('newResponsibleManager').set(self, manager)

    security.declareProtected(permissions.View, 'getIssueChanges')
    def getIssueChanges(self):
        """ Get a list of changes this response has made to the issue.

        Contains dicts with keys:

            id: A unique id for this change
            name: The field name that was changed
            before: The state of the field before
            after: The new state of the field
        """
        return tuple(getattr(self, '_issueChanges', []))

    # Manually created methods

    def _renameAfterCreation(self, check_auto_id=False):
        parent = self.aq_inner.aq_parent
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

    def _addIssueChange(self, id, name, before, after):
        """Add a new issue change"""
        delta = getattr(self, '_issueChanges', None)
        if not delta:
            self._issueChanges = []
            delta = self._issueChanges

        for d in delta:
            if d['id'] == id:
                d['name'] = name
                d['before'] = before
                d['after'] = after
                self._p_changed = 1
                return

        delta.append({'id': id,
                      'name': name,
                      'before': before,
                      'after': after})
        self._p_changed = 1

    security.declareProtected(permissions.View, 'getCurrentIssueSeverity')
    def getCurrentIssueSeverity(self):
        return self.aq_inner.aq_parent.getSeverity()

    security.declarePublic('isValid')
    def isValid(self):
        """Check if the response is valid.

        Meaning: a response has been filled in,
        """
        errors = {}
        self.Schema().validate(self, None, errors, 1, 1)

        if errors:
            return False

        if not self.getResponse() and not self.getIssueChanges():
            return False

        return True

    def Title(self):
        """Define title to be the same as response id. Responses have little
        value on their own anyway.
        """
        return self.getId()

    security.declareProtected(permissions.View, 'getCurrentTargetRelease')
    def getCurrentTargetRelease(self):
        return self.aq_inner.aq_parent.getTargetRelease()

    security.declareProtected(permissions.View, 'getCurrentResponsibleManager')
    def getCurrentResponsibleManager(self):
        return self.aq_inner.aq_parent.getResponsibleManager()

    def post_validate(self, REQUEST=None, errors=None):
        """Ensure that we have *something* in the response, be it an issue
        change or some text
        """

        if errors or REQUEST.get('_poi_validated', False):
            return

        # This is an annoying hack, but because this method gets called twice
        # by the AT machinery, we can't test for changes below when we get
        # called the second time.
        REQUEST.set('_poi_validated', True)

        text = REQUEST.get('response', None)
        if text:
            return

        newSeverity = REQUEST.get('newSeverity', None)
        newTargetRelease = REQUEST.get('newTargetRelease', None)
        newResponsibleManager = REQUEST.get('newResponsibleManager', None)
        transition = REQUEST.get('issueTransition', None)

        currentSeverity = self.getCurrentIssueSeverity()
        currentTargetRelease = self.getCurrentTargetRelease()
        currentResponsibleManager = self.getCurrentResponsibleManager()
        currentTransition = self.getIssueTransition()

        if newSeverity and newSeverity != currentSeverity:
            return
        if newTargetRelease and newTargetRelease != currentTargetRelease:
            return
        if newResponsibleManager and \
                newResponsibleManager != currentResponsibleManager:
            return
        if transition and transition != currentTransition:
            return

        # Nothing appears to be set, mark an error
        errors['response'] = 'Please provide a response'

    @instance.clearbefore
    def setResponse(self, *args, **kwargs):
        self.getField('response').set(self, *args, **kwargs)

    @instance.memoize
    def getTaggedResponse(self, **kwargs):
        # perform link detection
        text = self.getField('response').get(self, **kwargs)
        return self.aq_parent.linkDetection(text)

    def SearchableText(self):
        """Make sure we are not storing html escaped stuff.
        """
        return self.Title() + " " + self.getRawResponse()


registerType(PoiResponse, PROJECTNAME)
# end of class PoiResponse
