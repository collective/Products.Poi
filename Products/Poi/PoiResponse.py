# File: PoiResponse.py
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

from Products.Poi.interfaces.Response import Response


# additional imports from tagged value 'import'
import Permissions

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base
##/code-section module-header

schema= Schema((
    StringField('id',
            widget=StringWidget(
    visible={'edit' : 'invisible', 'view' : 'invisible'},
    modes=('view',),
    label='Id',
    label_msgid='Poi_label_id',
    description='Enter a value for id.',
    description_msgid='Poi_help_id',
    i18n_domain='Poi',
)        ,
        mode="r"    ),
    
    StringField('title',
            widget=StringWidget(
    label="Subject",
    description="""Enter a brief subject for this response, e.g. "Fixed" or "Will be fixed in next release".""",
    label_msgid='Poi_label_title',
    description_msgid='Poi_help_title',
    i18n_domain='Poi',
)        ,
        required=True        ,
        accessor="Title"    ),
    
    ComputedField('description',
            widget=ComputedWidget(
    visible={'view' : 'invisible', 'edit' : 'invisible'},
    label='Description',
    label_msgid='Poi_label_description',
    description='Enter a value for description.',
    description_msgid='Poi_help_description',
    i18n_domain='Poi',
)        ,
        expression="context.getResponse(mimetype='text/plain')[:50]"        ,
        accessor="Description"    ),
    
    TextField('response',
            allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',)        ,
        widget=RichWidget(
    label="Detailed response",
    description="Please enter your response below",
    rows="10",
    label_msgid='Poi_label_response',
    description_msgid='Poi_help_response',
    i18n_domain='Poi',
)        ,
        allowed_types=('text/structured', 'text/plain', 'text/html', 'text/restructured',)        ,
        default_content_type="text/structured"        ,
        default_output_type="text/html"        ,
        required=True    ),
    
    StringField('issueTransition',
            mutator="setNewIssueState"        ,
        widget=SelectionWidget(
    label="Change issue state",
    description="Select a change of state in the issue this response is for, if applicable",
    label_msgid='Poi_label_issueTransition',
    description_msgid='Poi_help_issueTransition',
    i18n_domain='Poi',
)        ,
        vocabulary='getAvailableIssueTransitions'        ,
        default=''        ,
        enforceVocabulary=False        ,
        accessor="getIssueTransition"    ),
    
),
)


##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiResponse(BaseContent):
    """
    A response to an issue, added by a project manager.
    
    When giving a response, the workflow state of the parent issue
    can be set at the same time.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),) + (Response,)


    # This name appears in the 'add' box
    archetype_name             = 'Response'

    meta_type    = 'PoiResponse' 
    portal_type  = 'PoiResponse' 
    allowed_content_types      = [] 
    filter_content_types       = 0
    global_allow               = 0
    allow_discussion           = 0
    content_icon               = 'PoiResponse.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    typeDescription            = "A project managers' response to an issue."
    typeDescMsgId              = 'description_edit_poiresponse'

    actions =  (


       {'action':      "string:$object_url/poi_response_view",
        'category':    "object",
        'id':          'view',
        'name':        'view',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

    )

    schema = BaseSchema + \
             schema

    ##code-section class-header #fill in your manual code here
    aliases = {
        '(Default)'  : 'poi_response_view',
        'view'       : 'poi_response_view',
        'edit'       : 'base_edit',
        'properties' : 'base_metadata',
        'sharing'    : 'folder_localrole_form'
    }
    ##/code-section class-header


    #Methods

    security.declareProtected(Permissions.ModifyPortalContent, 'setNewIssueState')
    def setNewIssueState(self,transition):
        """
        Set a new review state for the parent issue, by executing
        the given transition.
        """
        # XXX: Why are we being called twice if enforceVocabulary=1 (hence)
        #  vocab becomes invalid after first time...

        if transition and transition in self.getAvailableIssueTransitions():
            wftool = getToolByName(self, 'portal_workflow')
            self._issueStateBefore = wftool.getInfoFor(self.aq_parent,
                                                       'review_state')
            wftool.doActionFor(self.aq_parent, transition)
            self._issueStateAfter = wftool.getInfoFor(self.aq_parent,
                                                      'review_state')
            self._p_changed = 1

        self.getField('issueTransition').set(self, transition)

    security.declareProtected(Permissions.View, 'getIssueStateBefore')
    def getIssueStateBefore(self):
        """
        Get the state of the parent issue that was set before the
        response was added.
        """
        # Default to None if it was not set
        return getattr(aq_base(self), '_issueStateBefore', None)



    security.declarePublic('getIssueStateAfter')
    def getIssueStateAfter(self):
        """
        Get the state of the parent issue that was set before the
        response was added.
        """
        # Default to None if it was not set
        return getattr(aq_base(self), '_issueStateAfter', None)

    def processForm(self, data=1, metadata=0, REQUEST=None, values=None):
        isNew = self.checkCreationFlag()
        BaseObject.processForm(self, data, metadata, REQUEST, values)
        if isNew:
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
            get_transaction().commit(1)
            self.setId(newId)

def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiResponse,PROJECTNAME)
# end of class PoiResponse

##code-section module-footer #fill in your manual code here
##/code-section module-footer



