# -*- coding: utf-8 -*-
#
# File: PoiPscTracker.py
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

from Products.Archetypes.atapi import BaseFolder
from Products.Archetypes.atapi import BaseFolderSchema
from Products.Archetypes.atapi import DisplayList
from Products.Archetypes.atapi import registerType
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import StringWidget

from Products.Poi.content.PoiTracker import PoiTracker
from Products.CMFPlone.interfaces.NonStructuralFolder import \
    INonStructuralFolder
from Products.Poi.config import PROJECTNAME
from Products.Poi.config import PSC_TRACKER_ID

from Products.Poi import permissions

from Products.CMFCore.utils import getToolByName
import transaction
from zope.interface import implements
from Products.Poi.interfaces import ITracker

schema = Schema((

    StringField(
        name='id',
        widget=StringWidget(
            label="Short name",
            description="Short name for the tracker - should be 'issues' to comply with the standards.",
            label_msgid="Poi_label_psctracker_title",
            description_msgid="Poi_description_psctracker_title",
            i18n_domain='Poi',
        ),
        required=False,
        mode="r"
    ),

),
)

PoiPscTracker_schema = BaseFolderSchema.copy() + \
    getattr(PoiTracker, 'schema', Schema(())).copy() + \
    schema.copy()

PoiPscTracker_schema = PoiPscTracker_schema.copy()
del PoiPscTracker_schema['title']


class PoiPscTracker(PoiTracker):
    """Version of the PoiTracker which supports the
    PloneSoftwareCenter. Intended to be added inside a PSCProject.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder, '__implements__', ()), ) + \
        (getattr(PoiTracker, '__implements__', ()), ) + \
        (INonStructuralFolder, )
    implements(ITracker)

    # This name appears in the 'add' box
    archetype_name = 'Issue Tracker'

    meta_type = 'PoiPscTracker'
    portal_type = 'PoiPscTracker'
    allowed_content_types = [] + list(getattr(PoiTracker,
                                              'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 0
    content_icon = 'PoiTracker.gif'
    immediate_view = 'base_view'
    default_view = 'poi_tracker_view'
    suppl_views = ()
    typeDescription = "A simple issue tracker"
    typeDescMsgId = 'description_edit_poipsctracker'


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

    schema = PoiPscTracker_schema

    schema = schema.copy()
    del schema['availableReleases']

    # Methods

    security.declareProtected(permissions.View, 'getExternalTitle')
    def getExternalTitle(self):
        """ The external title of a PSC tracker is <Project> Issue Tracker."""
        return self.aq_inner.aq_parent.Title() + " Issue Tracker"

    def _renameAfterCreation(self, check_auto_id=False):
        parent = self.aq_inner.aq_parent
        if PSC_TRACKER_ID not in parent.objectIds():
            # Can't rename without a subtransaction commit when using
            # portal_factory!
            transaction.savepoint(optimistic=True)
            self.setId(PSC_TRACKER_ID)

    security.declareProtected(permissions.View, 'getAvailableReleases')
    def getAvailableReleases(self):
        """Get the UIDs of the releases available to the tracker."""
        catalog = getToolByName(self, 'portal_catalog')
        releases = catalog.searchResults(
                        portal_type = 'PSCRelease',
                        path = '/'.join(self.getPhysicalPath()[:-1]),
                        sort_on = 'created',
                        )
        return [r.UID for r in releases]

    security.declareProtected(permissions.View, 'getReleasesVocab')
    def getReleasesVocab(self):
        """Get the releases available to the tracker as a DisplayList."""
        catalog = getToolByName(self, 'portal_catalog')
        releases = catalog.searchResults(
                        portal_type = 'PSCRelease',
                        path = '/'.join(self.getPhysicalPath()[:-1]),
                        )
        return DisplayList([(r.UID, r.getId) for r in releases])

    security.declareProtected(permissions.View, 'Title')
    def Title(self):
        """The title of an issue tracker is always "Issue tracker"."""
        return "Issue tracker"


def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiPscTracker, PROJECTNAME)
# end of class PoiPscTracker
