"""Workflow: poi_issue_workflow
"""

# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
#

# Generator: ArchGenXML Version 1.4.0-beta1 devel
#            http://sf.net/projects/archetypes/
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

def setuppoi_issue_workflow(self, workflow):
    """Define the poi_issue_workflow workflow.
    """

    workflow.setProperties(title='poi_issue_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['closed', 'in-progress', 'postponed', 'open']:
        workflow.states.addState(s)

    for t in ['begin', 're-start', 're-open', 'close', 'postpone', 'hold']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    for p in []:
        workflow.addManagedPermission(p)
 
    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('open')

    ## States initialization

    stateDef = workflow.states['closed']
    stateDef.setProperties(title="""Issue closed""",
                           transitions=['re-open'])

    stateDef = workflow.states['in-progress']
    stateDef.setProperties(title="""Work in progresss""",
                           transitions=['close', 'postpone'])

    stateDef = workflow.states['postponed']
    stateDef.setProperties(title="""Postponed""",
                           transitions=['re-start', 're-open'])

    stateDef = workflow.states['open']
    stateDef.setProperties(title="""Open""",
                           transitions=['begin', 'hold', 'close'])

    ## Transitions initialization

    transitionDef = workflow.transitions['begin']
    transitionDef.setProperties(title="""Begin work""",
                                new_state_id="""in-progress""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Begin work""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['re-start']
    transitionDef.setProperties(title="""Begin work""",
                                new_state_id="""in-progress""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Begin work""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['re-open']
    transitionDef.setProperties(title="""Re-open""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Re-open""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['close']
    transitionDef.setProperties(title="""Close""",
                                new_state_id="""closed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Close""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['postpone']
    transitionDef.setProperties(title="""Postpone""",
                                new_state_id="""postponed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Postpone""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['hold']
    transitionDef.setProperties(title="""Put on hold""",
                                new_state_id="""postponed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Put on hold""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
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



def createpoi_issue_workflow(self, id):
    """Create the workflow for Poi.
    """
    
    ob = DCWorkflowDefinition(id)
    setuppoi_issue_workflow(self, ob)
    return ob

addWorkflowFactory(createpoi_issue_workflow,
                   id='poi_issue_workflow',
                   title='FirePoi Issue workflow')

##code-section create-workflow-module-footer #fill in your manual code here
##/code-section create-workflow-module-footer

