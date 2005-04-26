""" Workflow: poi_issue_workflow """

# Copyright (c) 2005 by None
#
# Generated: 
# Generator: ArchGenXML Version 1.4 devel 1
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
__author__    = '''unknown <unknown>'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod

productname = 'Poi'

def setuppoi_issue_workflow(self, wf):
    """
    poi_issue_workflow Workflow Definition
    """
    # add additional roles to portal
    portal=getToolByName(self,'portal_url').getPortalObject()
    data=list(portal.__ac_roles__)
    for role in []:
        if not role in self.__ac_roles__:
            data.append(role)
    portal.__ac_roles__=tuple(data)

    wf.setProperties(title='poi_issue_workflow')

    for s in ['closed', 'in-progress', 'postponed', 'open']:
        wf.states.addState(s)

    for t in ['begin', 're-start', 're-open', 'close', 'postpone', 'hold']:
        wf.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        wf.variables.addVariable(v)

    for p in []:
        wf.addManagedPermission(p)

    ## Initial State

    wf.states.setInitialState('open')

    ## States initialization

    sdef = wf.states['closed']
    sdef.setProperties(title="""Issue closed""",
                       transitions=['re-open'])

    sdef = wf.states['in-progress']
    sdef.setProperties(title="""Work in progresss""",
                       transitions=['close', 'postpone'])

    sdef = wf.states['postponed']
    sdef.setProperties(title="""Postponed""",
                       transitions=['re-start', 're-open'])

    sdef = wf.states['open']
    sdef.setProperties(title="""Open""",
                       transitions=['begin', 'hold', 'close'])

    ## Transitions initialization
        
    tdef = wf.transitions['begin']
    tdef.setProperties(title="""Begin work""",
                       new_state_id="""in-progress""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Begin work""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'View', 'guard_roles': 'Owner;Manager'},
                       )
        
    tdef = wf.transitions['re-start']
    tdef.setProperties(title="""Begin work""",
                       new_state_id="""in-progress""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Begin work""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'View', 'guard_roles': 'Owner;Manager'},
                       )
        
    tdef = wf.transitions['re-open']
    tdef.setProperties(title="""Re-open""",
                       new_state_id="""open""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Re-open""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'View', 'guard_roles': 'Owner;Manager'},
                       )
        
    tdef = wf.transitions['close']
    tdef.setProperties(title="""Close""",
                       new_state_id="""closed""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Close""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'View', 'guard_roles': 'Owner;Manager'},
                       )
        
    tdef = wf.transitions['postpone']
    tdef.setProperties(title="""Postpone""",
                       new_state_id="""postponed""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Postpone""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'View', 'guard_roles': 'Owner;Manager'},
                       )
        
    tdef = wf.transitions['hold']
    tdef.setProperties(title="""Put on hold""",
                       new_state_id="""postponed""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""Put on hold""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'View', 'guard_roles': 'Owner;Manager'},
                       )

    ## State Variable
    wf.variables.setStateVar('review_state')

    ## Variables initialization
    vdef = wf.variables['review_history']
    vdef.setProperties(description="""Provides access to workflow history""",
                       default_value="""""",
                       default_expr="""state_change/getHistory""",
                       for_catalog=0,
                       for_status=0,
                       update_always=0,
                       props={'guard_permissions': 'Request review; Review portal content'})

    vdef = wf.variables['comments']
    vdef.setProperties(description="""Comments about the last transition""",
                       default_value="""""",
                       default_expr="""python:state_change.kwargs.get('comment', '')""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['time']
    vdef.setProperties(description="""Time of the last transition""",
                       default_value="""""",
                       default_expr="""state_change/getDateTime""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['actor']
    vdef.setProperties(description="""The ID of the user who performed the last transition""",
                       default_value="""""",
                       default_expr="""user/getId""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)

    vdef = wf.variables['action']
    vdef.setProperties(description="""The last transition""",
                       default_value="""""",
                       default_expr="""transition/getId|nothing""",
                       for_catalog=0,
                       for_status=1,
                       update_always=1,
                       props=None)
                       
    # XXX Generation of worklists is not implemented yet...
    # in the meantime, you can use the protecte code section below to
    # do it manually    

    ##code-section custom-init-bottom #fill in your manual code here
    ##/code-section custom-init-bottom


def createpoi_issue_workflow(self, id):
    "..."
    ob = DCWorkflowDefinition(id)
    setuppoi_issue_workflow(self, ob)
    return ob

addWorkflowFactory(createpoi_issue_workflow,
                   id='poi_issue_workflow',
                   title='poi_issue_workflow')

