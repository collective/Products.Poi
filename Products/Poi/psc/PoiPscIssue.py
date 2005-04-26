# File: PoiPscIssue.py
"""\
Version of the PoiIssue which supports the PloneSoftwareCenter.
Intended to be used inside a PSCProject.

"""
# Copyright (c) 2005 by None
#
# Generator: ArchGenXML Version 1.4 devel 1 http://sf.net/projects/archetypes/
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
__author__  = '''unknown <unknown>'''
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.public import *


from Products.Poi.PoiIssue import PoiIssue


# additional imports from tagged value 'import'
from Products.Poi import Permissions

from Products.Poi.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema= Schema((
    ReferenceField('releases',
        widget=ReferenceWidget(
            description="If this issue is related to one or more releases, please select them here.",
            label="Releases",
            label_msgid='Poi_label_releases',
            description_msgid='Poi_help_releases',
            i18n_domain='Poi',
        ),
        allowed_types=('PSCRelease',),
        multiValued=1,
        relationship="issueRelatedToRelease",
        vocabulary='getAvailableReleases',
        enforceVocabulary=1,
    ),
    
    ReferenceField('proposals',
        widget=ReferenceWidget(
            label="Improvement proposals",
            description="If this issue is related to one or more improvement proposals, please select them here.",
            label_msgid='Poi_label_proposals',
            description_msgid='Poi_help_proposals',
            i18n_domain='Poi',
        ),
        allowed_types=('PSCImprovementProposal',),
        multiValued=1,
        relationship="issueRelatedToProposal",
        vocabulary='getAvailableProposals',
        enforceVocabulary=1,
    ),
    
),
)

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiPscIssue(BaseFolder,PoiIssue):
    """
    Version of the PoiIssue which supports the PloneSoftwareCenter.
    Intended to be used inside a PSCProject.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),) + (getattr(PoiIssue,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'Issue'
    portal_type = meta_type    = 'PoiPscIssue' 

    allowed_content_types      = ['PoiPscResponse'] 
    filter_content_types       = 1
    global_allow               = 0
    allow_discussion           = 0
    content_icon               = 'PoiIssue.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    typeDescription            = "An issue. Issues begin in the 'open' state, and can be responded to by project mangers."
    typeDescMsgId              = 'description_edit_poipscissue'

    actions =  (


       {'action':      "string:$object_url/poi_psc_issue_view",
        'category':    "object",
        'id':          'view',
        'name':        'poi_psc_issue_view',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

    )

    schema = BaseFolderSchema + \
             getattr(PoiIssue,'schema',Schema(())) + \
             schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

registerType(PoiPscIssue,PROJECTNAME)
# end of class PoiPscIssue

##code-section module-footer #fill in your manual code here
##/code-section module-footer



