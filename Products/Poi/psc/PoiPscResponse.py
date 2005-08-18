# File: PoiPscResponse.py
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

from Products.Poi.PoiResponse import PoiResponse


# additional imports from tagged value 'import'
from Products.Poi import Permissions

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
##/code-section module-header

schema= Schema((
    ReferenceField('releases',
            widget=ReferenceWidget(
    label="Releases",
    description="If this response is relevant to one or more releases, select them here.",
    label_msgid='Poi_label_releases',
    description_msgid='Poi_help_releases',
    i18n_domain='Poi',
)        ,
        allowed_types=('PSCRelease',)        ,
        relationship="responseRelatedToRelease"        ,
        multiValued=1        ,
        vocabulary='getAvailableReleases'        ,
        enforceVocabulary=1    ),
    
    ReferenceField('proposals',
            widget=ReferenceWidget(
    label="Improvement proposals",
    description="If this response is related to one or more improvement proposals, please select them here.",
    label_msgid='Poi_label_proposals',
    description_msgid='Poi_help_proposals',
    i18n_domain='Poi',
)        ,
        allowed_types=('PSCImprovementProposal',)        ,
        relationship="responseRelatedToProposal"        ,
        multiValued=1        ,
        vocabulary='getAvailableProposals'        ,
        enforceVocabulary=1    ),
    
),
)


##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiPscResponse(PoiResponse,BaseContent):
    """
    Version of the PoiResponse which supports the
    PloneSoftwareCenter.
    Intended to be used inside a PSCProject.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(PoiResponse,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)


    # This name appears in the 'add' box
    archetype_name             = 'Response'

    meta_type    = 'PoiPscResponse' 
    portal_type  = 'PoiPscResponse' 
    allowed_content_types      = [] + list(getattr(PoiResponse, 'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 0
    allow_discussion           = 0
    content_icon               = 'PoiResponse.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    typeDescription            = "A project managers' response to an issue."
    typeDescMsgId              = 'description_edit_poipscresponse'

    actions =  (


       {'action':      "string:$object_url/poi_psc_response_view",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

    )

    schema = BaseSchema + \
             getattr(PoiResponse,'schema',Schema(())) + \
             schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods
def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiPscResponse,PROJECTNAME)
# end of class PoiPscResponse

##code-section module-footer #fill in your manual code here
##/code-section module-footer



