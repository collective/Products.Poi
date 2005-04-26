# File: PoiTracker.py
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


from Products.Poi.interfaces.Tracker import Tracker


# additional imports from tagged value 'import'
from Products.ArchAddOn.Fields import SimpleDataGridField
import Permissions
from Products.ArchAddOn.Widgets import SimpleDataGridWidget

from Products.Poi.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section module-header

schema= Schema((
    StringField('title',
        widget=StringWidget(
            label="Tracker name",
            description="Enter a descriptive name for this tracker",
            label_msgid='Poi_label_title',
            description_msgid='Poi_help_title',
            i18n_domain='Poi',
        ),
        required=1,
        accessor="Title",
    ),
    
    TextField('description',
        widget=TextAreaWidget(
            label="Tracker description",
            description="Describe the purpose of this tracker",
            label_msgid='Poi_label_description',
            description_msgid='Poi_help_description',
            i18n_domain='Poi',
        ),
        accessor="Description",
    ),
    
    SimpleDataGridField('categories',
        default=['bug | Bug | Functionality bugs in the software', 'ui | User interface | User interface problems', 'performance | Performance | Performance issues'],
        widget=SimpleDataGridWidget(
            label="Categories",
            description="""Enter the issue categories for this tracker, one specification per line. The format is "Short name | Title | Description".""",
            label_msgid='Poi_label_categories',
            description_msgid='Poi_help_categories',
            i18n_domain='Poi',
        ),
        column_names=('id', 'title', 'description'),
        columns=3,
    ),
    
),
)

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiTracker(BaseFolder):
    """
    The default tracker
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseFolder,'__implements__',()),) + (Tracker,)


    # This name appears in the 'add' box
    archetype_name             = 'Tracker'
    portal_type = meta_type    = 'PoiTracker' 

    allowed_content_types      = ['PoiIssue'] 
    filter_content_types       = 1
    global_allow               = 1
    allow_discussion           = 0
    content_icon               = 'PoiTracker.gif'
    immediate_view             = 'base_view'
    default_view               = 'base_view'
    typeDescription            = "An issue tracker"
    typeDescMsgId              = 'description_edit_poitracker'

    actions =  (


       {'action':      "string:$object_url/poi_tracker_view",
        'category':    "object",
        'id':          'view',
        'name':        'poi_tracker_view',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

    )

    schema = BaseFolderSchema + \
             schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

    security.declareProtected(Permissions.View, 'getCategoryIds')
    def getCategoryIds(self):
        """
        Get a list of all category ids in the tracker.
        """
        return self.getField('categories').getColumn(self, 0)


    security.declareProtected(Permissions.View, 'getFilteredIssues')
    def getFilteredIssues(self,category,state):
        """
        Get the contained issues in the given category and review 
        state. If either is None, return all categories/states.
        """
        
        catalog = getToolByName(self, 'portal_catalog')
        
        query                = {}
        query['path']        = '/'.join(self.getPhysicalPath())
        query['portal_type'] = ['PoiIssue', 'PoiPscIssue']
        
        if category:
            query['getCategories'] = category
        if state:
            query['review_state']  = state
            
        query['sort_on'] = 'Date'
        
        return catalog.searchResults(query)


    security.declareProtected(Permissions.AddIssue, 'generateUniqueId')
    def generateUniqueId(self, typeName):
        """
        Give issues sequential integers ids
        """
        
        idx = 0
        ids = self.contentIds()
        
        while "%d" % (idx,) in ids:
            idx += 1
        
        return "%d" % (idx,)


registerType(PoiTracker,PROJECTNAME)
# end of class PoiTracker

##code-section module-footer #fill in your manual code here
##/code-section module-footer



