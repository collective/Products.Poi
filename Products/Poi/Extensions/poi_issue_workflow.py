# -*- coding: utf-8 -*-
#
# File: Poi.py
#
# Copyright (c) 2006 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.5.0 svn/devel
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Martin Aspeli <optilude@gmx.net>"""
__docformat__ = 'plaintext'


from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.Poi.config import *

##code-section create-workflow-module-header #fill in your manual code here
##/code-section create-workflow-module-header


productname = 'Poi'

def setuppoi_issue_workflow(self, workflow):
    """Define the poi_issue_workflow workflow.
    """

    workflow.setProperties(title='poi_issue_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['resolved', 'in-progress', 'postponed', 'rejected', 'open', 'closed', 'unconfirmed', 'new']:
        workflow.states.addState(s)

    for t in ['begin-open', 'open-rejected', 'postpone-unconfirmed', 'open-postponed', 're-start', 'reject-open', 'post', 'reject-unconfirmed', 'hold-open', 'open-closed', 'confirm-resolved', 'resolve-in-progress', 'resolve-unconfirmed', 'postpone', 'resolve-open', 'open-resolved', 'accept-unconfirmed']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('Delete objects')
    workflow.addManagedPermission('Poi: Modify issue state')
    workflow.addManagedPermission('Modify portal content')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('new')

    ## States initialization

    stateDef = workflow.states['resolved']
    stateDef.setProperties(title="""Resolved""",
                           transitions=['open-resolved', 'confirm-resolved'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['in-progress']
    stateDef.setProperties(title="""In progress""",
                           transitions=['resolve-in-progress', 'postpone'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['postponed']
    stateDef.setProperties(title="""Postponed""",
                           transitions=['re-start', 'open-postponed'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['rejected']
    stateDef.setProperties(title="""Rejected""",
                           transitions=['open-rejected'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['open']
    stateDef.setProperties(title="""Confirmed""",
                           transitions=['begin-open', 'hold-open', 'resolve-open', 'reject-open'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['closed']
    stateDef.setProperties(title="""Tested and confirmed closed""",
                           transitions=['open-closed'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['unconfirmed']
    stateDef.setProperties(title="""Unconfirmed""",
                           transitions=['accept-unconfirmed', 'reject-unconfirmed', 'postpone-unconfirmed', 'resolve-unconfirmed'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['new']
    stateDef.setProperties(title="""Being created""",
                           transitions=['post'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])
    stateDef.setPermission('Poi: Modify issue state',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])

    ## Transitions initialization

    transitionDef = workflow.transitions['begin-open']
    transitionDef.setProperties(title="""Begin work""",
                                new_state_id="""in-progress""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Begin work""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['open-rejected']
    transitionDef.setProperties(title="""Open""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Open""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['postpone-unconfirmed']
    transitionDef.setProperties(title="""Postpone""",
                                new_state_id="""postponed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Postpone""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['open-postponed']
    transitionDef.setProperties(title="""Re-open""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Re-open""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
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
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['reject-open']
    transitionDef.setProperties(title="""Reject""",
                                new_state_id="""rejected""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Reject""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['sendInitialEmail']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.poi_issue_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['post']
    transitionDef.setProperties(title="""Post issue on save""",
                                new_state_id="""unconfirmed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""sendInitialEmail""",
                                actbox_name="""Post issue on save""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_expr': 'here/isValid'},
                                )

    transitionDef = workflow.transitions['reject-unconfirmed']
    transitionDef.setProperties(title="""Reject""",
                                new_state_id="""rejected""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Reject""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['hold-open']
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

    transitionDef = workflow.transitions['open-closed']
    transitionDef.setProperties(title="""Re-open""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Re-open""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['confirm-resolved']
    transitionDef.setProperties(title="""Confirm resolved""",
                                new_state_id="""closed""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Confirm resolved""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['sendResolvedMail']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.poi_issue_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['resolve-in-progress']
    transitionDef.setProperties(title="""Resolve""",
                                new_state_id="""resolved""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""sendResolvedMail""",
                                actbox_name="""Resolve""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['resolve-unconfirmed']
    transitionDef.setProperties(title="""Resolve immediately""",
                                new_state_id="""resolved""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Resolve immediately""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
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
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['sendResolvedMail']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.poi_issue_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['resolve-open']
    transitionDef.setProperties(title="""Resolve""",
                                new_state_id="""resolved""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""sendResolvedMail""",
                                actbox_name="""Resolve""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['open-resolved']
    transitionDef.setProperties(title="""Re-open""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Re-open""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
                                )

    transitionDef = workflow.transitions['accept-unconfirmed']
    transitionDef.setProperties(title="""Open""",
                                new_state_id="""open""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Open""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_permissions': 'Poi: Modify issue state'},
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

