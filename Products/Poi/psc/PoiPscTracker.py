# File: PoiPscTracker.py
# 
# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.4.0-beta1 devel http://sf.net/projects/archetypes/
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

from Products.Poi.PoiTracker import PoiTracker


# additional imports from tagged value 'import'
from Products.Poi import Permissions

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema= Schema((
),
)


##code-section after-schema #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section after-schema

class PoiPscTracker(PoiTracker,BaseFolder):
    """
    Version of the PoiTracker which supports the
    PloneSoftwareCenter. 
    Intended to be added inside a PSCProject.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(PoiTracker,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'Issue tracker'

    meta_type    = 'PoiPscTracker' 
    portal_type  = 'PoiPscTracker' 
    allowed_content_types      = ['PoiPscIssue'] 
    filter_content_types       = 1
    global_allow               = 0
    allow_discussion           = 0
    content_icon               = 'PoiTracker.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    typeDescription            = "A simple issue tracker"
    typeDescMsgId              = 'description_edit_poipsctracker'

    actions =  (


       {'action':      "string:$object_url/poi_tracker_view",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

    )

    schema = BaseFolderSchema + \
             getattr(PoiTracker,'schema',Schema(())) + \
             schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

    security.declareProtected(Permissions.View, 'getAvailableReleases')
    def getAvailableReleases(self):
        """
        Get the releases available to the tracker
        """
        catalog = getToolByName(self, 'portal_catalog')
        releases = catalog.searchResults(
                        portal_type = 'PSCRelease',
                        path = '/'.join(self.getPhysicalPath()[:-1]),
                        )
        return DisplayList([(r.UID, r.Title) for r in releases])



    security.declareProtected(Permissions.View, 'getAvailableProposals')
    def getAvailableProposals(self):
        """
        Get the improvement proposals available to the tracker.
        """
        catalog = getToolByName(self, 'portal_catalog')
        proposals = catalog.searchResults(
                        portal_type = 'PSCImprovementProposal',
                        path = '/'.join(self.getPhysicalPath()[:-1]),
                        )
        return DisplayList([(p.UID, p.Title) for p in proposals])



registerType(PoiPscTracker,PROJECTNAME)
# end of class PoiPscTracker

##code-section module-footer #fill in your manual code here
##/code-section module-footer



