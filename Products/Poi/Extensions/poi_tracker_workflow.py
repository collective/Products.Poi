"""Workflow: poi_tracker_workflow
"""

# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
#

# Generator: ArchGenXML Version 1.4.0-beta2 devel
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
__author__    = '''Martin Aspeli <optilude@gmx.net>'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod

##code-section create-workflow-module-header #fill in your manual code here
##/code-section create-workflow-module-header


productname = 'Poi'

def setuppoi_tracker_workflow(self, workflow):
    """Define the poi_tracker_workflow workflow.
    """

    workflow.setProperties(title='poi_tracker_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['open', 'closed']:
        workflow.states.addState(s)

    for t in ['close', 'open']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    for p in ['Add Poi Issues', 'Add Poi Responses', 'View', 'Modify portal content', 'Access contents information', 'Add portal content', 'Add PoiIssues', 'Add PoiResponses']:
        workflow.addManagedPermission(p)

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('closed')

    ## States initialization

    stateDef = workflow.states['open']
    stateDef.setProperties(title="""Open for submissions""",
                           transitions=['close'])
    stateDef.setPermission('Add Poi Issues',
                           0,
                           ['Member', 'Manager', 'Owner'])
    stateDef.setPermission('Add Poi Responses',
                           0,
                           ['Member', 'Manager', 'Owner'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Member', 'Manager', 'Owner'])

    stateDef = workflow.states['closed']
    stateDef.setProperties(title="""Closed for submissions""",
                           transitions=['open'])
    stateDef.setPermission('Add PoiIssues',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Add PoiResponses',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Manager', 'Owner'])

    ## Transitions initialization

    transitionDef = workflow.transitions['close']
    transitionDef.setProperties(title="""Close tracker""",
                                new_state_id="""closed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Close tracker""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Owner; Manager'},
                                )

    transitionDef = workflow.transitions['open']
    transitionDef.setProperties(title="""Open tracker""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Open tracker""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Owner; Manager'},
                                )

    ## State Variable
    workflow.variables.setStateVar('review_state')

    ## Variables initialization
    variableDef = workflow.variables['review_history']
    variableDef.setProperties(description="""Provides access to workflow history""",
                              default_value="""""",
                              default_expr="""state_change/getHistory""",
                              for_catalog=0,
                              for_status=0,
                              update_always=0,
                              props={'guard_permissions': 'Request review; Review portal content'})

    variableDef = workflow.variables['comments']
    variableDef.setProperties(description="""Comments about the last transition""",
                              default_value="""""",
                              default_expr="""python:state_change.kwargs.get('comment', '')""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['time']
    variableDef.setProperties(description="""Time of the last transition""",
                              default_value="""""",
                              default_expr="""state_change/getDateTime""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['actor']
    variableDef.setProperties(description="""The ID of the user who performed the last transition""",
                              default_value="""""",
                              default_expr="""user/getId""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['action']
    variableDef.setProperties(description="""The last transition""",
                              default_value="""""",
                              default_expr="""transition/getId|nothing""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    ## Worklists Initialization


    # WARNING: below protected section is deprecated.
    # Add a tagged value 'worklist' with the worklist name to your state(s) instead.

    ##code-section create-workflow-setup-method-footer #fill in your manual code here
    ##/code-section create-workflow-setup-method-footer



def createpoi_tracker_workflow(self, id):
    """Create the workflow for Poi.
    """
    
    ob = DCWorkflowDefinition(id)
    setuppoi_tracker_workflow(self, ob)
    return ob

addWorkflowFactory(createpoi_tracker_workflow,
                   id='poi_tracker_workflow',
                   title='FirePoi Tracker workflow')

##code-section create-workflow-module-footer #fill in your manual code here
##/code-section create-workflow-module-footer

