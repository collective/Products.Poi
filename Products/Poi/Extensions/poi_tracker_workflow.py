""" Workflow: poi_tracker_workflow """

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

def setuppoi_tracker_workflow(self, wf):
    """
    poi_tracker_workflow Workflow Definition
    """
    # add additional roles to portal
    portal=getToolByName(self,'portal_url').getPortalObject()
    data=list(portal.__ac_roles__)
    for role in []:
        if not role in self.__ac_roles__:
            data.append(role)
    portal.__ac_roles__=tuple(data)

    wf.setProperties(title='poi_tracker_workflow')

    for s in ['open', 'closed']:
        wf.states.addState(s)

    for t in ['close', 'open']:
        wf.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        wf.variables.addVariable(v)

    for p in [u'Add FirePoi Issues', u'Add FirePoi Responses', 'View', 'Modify portal content', 'Access contents information']:
        wf.addManagedPermission(p)

    ## Initial State

    wf.states.setInitialState('closed')

    ## States initialization

    sdef = wf.states['open']
    sdef.setProperties(title="""Open for submissions""",
                       transitions=['close'])
    sdef.setPermission('Add FirePoi Issues', 0, ['Member', 'Manager', 'Owner'])
    sdef.setPermission('Add FirePoi Responses', 0, ['Manager'])
    sdef.setPermission('View', 0, ['Anonymous', 'Member', 'Manager', 'Owner'])
    sdef.setPermission('Modify portal content', 0, ['Owner', 'Manager'])
    sdef.setPermission('Access contents information', 0, ['Anonymous', 'Member', 'Manager', 'Owner'])

    sdef = wf.states['closed']
    sdef.setProperties(title="""Closed for submissions""",
                       transitions=['open'])
    sdef.setPermission('Add FirePoi Issues', 0, ['Manager'])
    sdef.setPermission('Add FirePoi Responses', 0, ['Manager'])
    sdef.setPermission('View', 0, ['Member', 'Manager', 'Owner'])
    sdef.setPermission('Modify portal content', 0, ['Manager', 'Owner'])
    sdef.setPermission('Access contents information', 0, ['Member', 'Manager', 'Owner'])

    ## Transitions initialization
        
    tdef = wf.transitions['close']
    tdef.setProperties(title="""close""",
                       new_state_id="""closed""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""""",
                       actbox_name="""close""",
                       actbox_url="""""",
                       actbox_category="""workflow""",
                       props={'guard_permissions': 'View', 'guard_roles': 'Owner;Manager'},
                       )
        
    ##creation of workflow scripts
    for wf_scriptname in ['giveManagerLocalrole']:
        if not wf_scriptname in wf.scripts.objectIds():
            wf.scripts._setObject(wf_scriptname,ExternalMethod(wf_scriptname, wf_scriptname, 
                productname + '.poi_tracker_workflow_scripts',
                wf_scriptname))
    
    tdef = wf.transitions['open']
    tdef.setProperties(title="""open""",
                       new_state_id="""open""",
                       trigger_type=1,
                       script_name="""""",
                       after_script_name="""giveManagerLocalrole""",
                       actbox_name="""open""",
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


def createpoi_tracker_workflow(self, id):
    "..."
    ob = DCWorkflowDefinition(id)
    setuppoi_tracker_workflow(self, ob)
    return ob

addWorkflowFactory(createpoi_tracker_workflow,
                   id='poi_tracker_workflow',
                   title='poi_tracker_workflow')

