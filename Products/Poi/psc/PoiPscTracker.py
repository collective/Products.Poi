# File: PoiPscTracker.py
# 
# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.4.0-RC2 svn/development 
#            http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''Martin Aspeli <optilude@gmx.net>'''
__docformat__ = 'plaintext'


from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.Poi.content.PoiTracker import PoiTracker
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder


# additional imports from tagged value 'import'
from Products.Poi import permissions

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema=Schema((
    StringField('id',
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

    StringField('title',
        widget=StringWidget(
            label="Title",
            description="Please enter the title of the tracker, or leave the default as shown below.",
            label_msgid="Poi_label_psctracker_title",
            description_msgid="Poi_label_psctracker_description",
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title",
        default_method="getDefaultTitle"
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PoiPscTracker_schema = BaseFolderSchema + \
    getattr(PoiTracker,'schema',Schema(())) + \
    schema

##code-section after-schema #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section after-schema

class PoiPscTracker(PoiTracker,BaseFolder):
    """
    Version of the PoiTracker which supports the
    PloneSoftwareCenter. Intended to be added inside a PSCProject.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(PoiTracker,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),) + (INonStructuralFolder,)


    # This name appears in the 'add' box
    archetype_name             = 'Issue Tracker'

    meta_type                  = 'PoiPscTracker'
    portal_type                = 'PoiPscTracker'
    allowed_content_types      = [] + list(getattr(PoiTracker, 'allowed_content_types', []))
    filter_content_types       = 1
    global_allow               = 0
    allow_discussion           = 0
    content_icon               = 'PoiTracker.gif'
    immediate_view             = 'base_view'
    default_view               = 'poi_tracker_view'
    suppl_views                = ()
    typeDescription            = "A simple issue tracker"
    typeDescMsgId              = 'description_edit_poipsctracker'

    actions =  (


       {'action':      "string:${object_url}",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': (permissions.View,),
        'condition'  : 'python:1'
       },


       {'action':      "string:${object_url}/edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': (permissions.ModifyPortalContent,),
        'condition'  : 'python:1'
       },


    )

    _at_rename_after_creation  = False

    schema = PoiPscTracker_schema

    ##code-section class-header #fill in your manual code here
    schema = schema.copy()
    del schema['availableReleases']
    ##/code-section class-header


    #Methods
    #manually created methods

    def getDefaultTitle(self):
        """Set the default title to <Project Name> Issues"""
        # we may be inside the portal_factory, so aq_parent may not be
        # enough
        parent = self.aq_parent
        while parent.getTypeInfo().getId() != 'PSCProject':
            parent = parent.aq_parent
            if parent is None:
                return "Issues"
        return parent.Title() + " Issues"


    security.declareProtected(permissions.View, 'getReleasesVocab')
    def getReleasesVocab(self):
        """
        Get the releases available to the tracker as a DisplayList
        """
        catalog = getToolByName(self, 'portal_catalog')
        releases = catalog.searchResults(
                        portal_type = 'PSCRelease',
                        path = '/'.join(self.getPhysicalPath()[:-1]),
                        )
        return DisplayList([(r.UID, r.getId) for r in releases])


    security.declareProtected(permissions.View, 'getAvailableReleases')
    def getAvailableReleases(self):
        """
        Get the UIDs of the releases available to the tracker
        """
        catalog = getToolByName(self, 'portal_catalog')
        releases = catalog.searchResults(
                        portal_type = 'PSCRelease',
                        path = '/'.join(self.getPhysicalPath()[:-1]),
                        )
        return [r.UID for r in releases]


def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiPscTracker,PROJECTNAME)
# end of class PoiPscTracker

##code-section module-footer #fill in your manual code here
##/code-section module-footer



