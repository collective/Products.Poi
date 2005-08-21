# File: PoiTracker.py
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

from Products.Poi.interfaces.Tracker import Tracker


# additional imports from tagged value 'import'
from Products.ArchAddOn.Fields import SimpleDataGridField
import Permissions
from Products.ArchAddOn.Widgets import SimpleDataGridWidget

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section module-header

schema=Schema((
    StringField('title',
        widget=StringWidget(
            label="Tracker name",
            description="Enter a descriptive name for this tracker",
            label_msgid='Poi_label_title',
            description_msgid='Poi_help_title',
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title"
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
        disable_polymorphing="1"
    ),
    
    SimpleDataGridField('availableTopics',
        default=['ui | User interface | User interface issues', 'functionality | Functionality| Issues with the basic functionality', 'process | Process | Issues relating to the development process itself'],
        widget=SimpleDataGridWidget(
            label="Topics",
            description="""Enter the issue topics/areas for this tracker, one specification per line. The format is "Short name | Title | Description".""",
            label_msgid='Poi_label_availableTopics',
            description_msgid='Poi_help_availableTopics',
            i18n_domain='Poi',
        ),
        column_names=('id', 'title', 'description',),
        columns=3,
        required=True
    ),
    
    SimpleDataGridField('availableCategories',
        default=['bug | Bug | Functionality bugs in the software', 'feature | Feature | Suggested features', 'patch | Patch | Patches to the software'],
        widget=SimpleDataGridWidget(
            label="Categories",
            description="""Enter the issue categories for this tracker, one specification per line. The format is "Short name | Title | Description".""",
            label_msgid='Poi_label_availableCategories',
            description_msgid='Poi_help_availableCategories',
            i18n_domain='Poi',
        ),
        column_names=('id', 'title', 'description'),
        columns=3,
        required=True
    ),
    
    LinesField('availableSeverities',
        default=['Critical', 'Important', 'Medium', 'Low'],
        widget=LinesWidget(
            label="Available severities",
            description="Enter the different type of issue severities that should be available, one per line.",
            label_msgid='Poi_label_availableSeverities',
            description_msgid='Poi_help_availableSeverities',
            i18n_domain='Poi',
        ),
        required=True
    ),
    
    StringField('defaultSeverity',
        default='Medium',
        widget=SelectionWidget(
            label="Default severity",
            description="Select the default severity for new issues.",
            label_msgid='Poi_label_defaultSeverity',
            description_msgid='Poi_help_defaultSeverity',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        vocabulary='getAvailableSeverities',
        required=True
    ),
    
    LinesField('availableReleases',
        widget=LinesWidget(
            label="Available releases",
            description="Enter the releases which issues can be assigned to, one per line",
            label_msgid='Poi_label_availableReleases',
            description_msgid='Poi_help_availableReleases',
            i18n_domain='Poi',
        ),
        required=True
    ),
    
    LinesField('managers',
        widget=LinesWidget(
            label="Tracker managers",
            description="Enter the user ids of the users who will be allowed to manage this tracker, one per line.",
            label_msgid='Poi_label_managers',
            description_msgid='Poi_help_managers',
            i18n_domain='Poi',
        )
    ),
    
    BooleanField('emailManagers',
        default=True,
        widget=BooleanWidget(
            label="Email tracker managers when there is tracker activity",
            description="If selected, tracker managers will receive an email each time a new issue or response is posted.",
            label_msgid='Poi_label_emailManagers',
            description_msgid='Poi_help_emailManagers',
            i18n_domain='Poi',
        )
    ),
    
),
)


##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiTracker(BaseBTreeFolder):
    """
    The default tracker
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseBTreeFolder,'__implements__',()),) + (Tracker,)


    # This name appears in the 'add' box
    archetype_name             = 'Tracker'

    meta_type                  = 'PoiTracker' 
    portal_type                = 'PoiTracker' 
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


       {'action':      "string:${object_url}",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

       {'action':      "string:${object_url}/edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': (Permissions.ModifyPortalContent,),
        'condition'  : 'python:1'
       },
        

    )

    schema = BaseFolderSchema + \
             schema

    ##code-section class-header #fill in your manual code here
    _at_rename_after_creation = True
    aliases = {
        '(Default)'  : 'poi_tracker_view',
        'view'       : 'poi_tracker_view',
        'edit'       : 'base_edit',
        'properties' : 'base_metadata',
        'sharing'    : 'folder_localrole_form'
    }
    ##/code-section class-header


    #Methods

    security.declareProtected(Permissions.View, 'getCategoryIds')
    def getCategoryIds(self):
        """
        Get a list of all category ids in the tracker.
        """
        return self.getField('availableCategories').getColumn(self, 0)



    security.declareProtected(Permissions.View, 'getFilteredIssues')
    def getFilteredIssues(self, criteria=None, **kwargs):
        """
        Get the contained issues in the given criteria.
        """

        if criteria is None:
            criteria = kwargs

        catalog = getToolByName(self, 'portal_catalog')

        query                = {}
        query['path']        = '/'.join(self.getPhysicalPath())
        query['portal_type'] = ['PoiIssue', 'PoiPscIssue']

        if criteria.has_key('release'):
            query['getRelease'] = criteria.get('release')
        if criteria.has_key('topic'):
            query['getTopic'] = criteria.get('topic')
        if criteria.has_key('category'):
            query['getCategory'] = criteria.get('category')
        if criteria.has_key('severity'):
            query['getSeverity'] = criteria.get('severity')
        if criteria.has_key('state'):
            query['review_state']  = criteria.get('state')
        if criteria.has_key('responsible'):
            query['getResponsibleManager']  = criteria.get('responsible')
        if criteria.has_key('text'):
            query['SearchableText']  = criteria.get('text')

        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')

        return catalog.searchResults(query)


    #manually created methods

    security.declareProtected(Permissions.View, 'getTopicIds')
    def getTopicIds(self):
        """
        Get a list of all topic ids in the tracker.
        """
        return self.getField('availableTopics').getColumn(self, 0)


    security.declareProtected(Permissions.ModifyPortalContent, 'setManagers')
    def setManagers(self, managers):
        """
        Set the list of tracker managers, and give them the Manager local role.
        """
        field = self.getField('managers')
        currentManagers = field.get(self)
        field.set(self, managers)

        toRemove = [m for m in currentManagers if m not in managers]
        toAdd = [m for m in managers if m not in currentManagers]
        if toRemove:
            self.manage_delLocalRoles(toRemove)
        for userId in toAdd:
            self.manage_setLocalRoles(userId, ['Manager'])


    def validate_managers(self, value):
        """Make sure issue tracker managers are actual user ids"""
        membership = getToolByName(self, 'portal_membership')
        notFound = []
        for userId in value:
            member = membership.getMemberById(userId)
            if member is None:
                notFound.append(userId)
        if notFound:
            return "The following user ids could not be found: %s" % ','.join(notFound)
        else:
            return None


    security.declarePublic('getIssueWorkflowStates')
    def getIssueWorkflowStates(self):
        """Get a DisplayList of the workflow states available on issues"""
        portal_workflow = getToolByName(self, 'portal_workflow')
        chain = portal_workflow.getChainForPortalType('PoiIssue')
        workflow = getattr(portal_workflow, chain[0])
        states = getattr(workflow, 'states')
        vocab = DisplayList()
        for id, state in states.items():
            vocab.add(id, state.title)
        return vocab.sortedByValue()


def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiTracker,PROJECTNAME)
# end of class PoiTracker

##code-section module-footer #fill in your manual code here
##/code-section module-footer



