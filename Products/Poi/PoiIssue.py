# File: PoiIssue.py
"""\
The default tracker

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


from Products.Poi.interfaces.Issue import Issue


# additional imports from tagged value 'import'
import Permissions

from Products.Poi.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema= Schema((
    StringField('id',
        widget=StringWidget(
            visible={'view' : 'invisible', 'edit': 'visible'},
            modes=('view',),
            label='Id',
            label_msgid='Poi_label_id',
            description='Enter a value for id.',
            description_msgid='Poi_help_id',
            i18n_domain='Poi',
        ),
        mode="r",
    ),
    
    StringField('title',
        widget=StringWidget(
            label="Title",
            description="Enter a short, descriptive title for the issue. A good title will make it easier for project managers to identify and respond to the issue.",
            label_msgid='Poi_label_title',
            description_msgid='Poi_help_title',
            i18n_domain='Poi',
        ),
        required=1,
        accessor="Title",
    ),
    
    TextField('description',
        widget=TextAreaWidget(
            label="Overview",
            description="Enter a brief overview of the issue. As with the title, a consise, meaningful description will make it easier for project managers to assess and respond to the issue.",
            label_msgid='Poi_label_description',
            description_msgid='Poi_help_description',
            i18n_domain='Poi',
        ),
        required=1,
        accessor="Description",
    ),
    
    LinesField('categories',
        widget=MultiSelectionWidget(
            label="Categories",
            description="Select the category or categories (if applicable) this issue is relevant to.",
            label_msgid='Poi_label_categories',
            description_msgid='Poi_help_categories',
            i18n_domain='Poi',
        ),
        enforceVocabulary=1,
        multiValued=1,
        vocabulary='getCategoriesVocab',
        required=1,
        schema="KeywordIndex:schema",
    ),
    
    TextField('details',
        allowable_content_types=('text/plain','text/structured','text/html','application/msword',),
        widget=RichWidget(
            label="Details",
            description="Please provide further details",
            rows="""10
            python:('text/structured', 'text/plain', 'text/html', 'text/restructured')""",
            label_msgid='Poi_label_details',
            description_msgid='Poi_help_details',
            i18n_domain='Poi',
        ),
        default_output_type="text/html",
        default_content_type="text/structured",
        required=1,
    ),
    
    LinesField('steps',
        widget=LinesWidget(
            label="Steps to reproduce",
            description="If applicable, please provide the steps to reproduce the error or identify the issue, one per line.",
            label_msgid='Poi_label_steps',
            description_msgid='Poi_help_steps',
            i18n_domain='Poi',
        ),
    ),
    
    StringField('contactEmail',
        widget=StringWidget(
            label="Contact email address",
            description="Optionally, provide an email address where you can be contacted for further information or when a resolution is available.",
            label_msgid='Poi_label_contactEmail',
            description_msgid='Poi_help_contactEmail',
            i18n_domain='Poi',
        ),
        validators=('isEmail',),
    ),
    
),
)

##code-section after-schema #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section after-schema

class PoiIssue(BaseFolder):
    """
    The default tracker
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),) + (Issue,)


    # This name appears in the 'add' box
    archetype_name             = 'Issue'
    portal_type = meta_type    = 'PoiIssue' 

    allowed_content_types      = ['PoiResponse'] 
    filter_content_types       = 1
    global_allow               = 0
    allow_discussion           = 0
    content_icon               = 'PoiIssue.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    typeDescription            = "An issue. Issues begin in the 'open' state, and can be responded to by project mangers."
    typeDescMsgId              = 'description_edit_poiissue'

    actions =  (


       {'action':      "string:$object_url/poi_issue_view",
        'category':    "object",
        'id':          'view',
        'name':        'poi_issue_view',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

    )

    schema = BaseFolderSchema + \
             schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

    security.declareProtected(Permissions.AddResponse, 'generateUniqueId')
    def generateUniqueId(self, typeName):
        """
        Give responses sequential integer ids.
        """
        
        idx = 0
        ids = self.contentIds()
        
        while "%d" % (idx,) in ids:
            idx += 1
        
        return "%d" % (idx,)


    security.declareProtected(Permissions.View, 'getCurrentIssueState')
    def getCurrentIssueState(self):
        """
        Get the current state of the issue.
        
        Used by PoiResponse to select a default for the new issue
        state selector.
        """
        
        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'review_state')


    security.declareProtected(Permissions.View, 'getAvailableIssueTransitions')
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


    security.declareProtected(Permissions.ModifyPortalContent, 'getCategoriesVocab')
    def getCategoriesVocab(self):
        """
        Get the categories available as a DisplayList.
        """

        field = self.aq_parent.getField('categories')
        return field.getAsDisplayList(self.aq_parent)


registerType(PoiIssue,PROJECTNAME)
# end of class PoiIssue

##code-section module-footer #fill in your manual code here
##/code-section module-footer



