from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

def installWorkflows(self, package, out):
    """
    """
    
    productname = 'Poi'
    workflowTool = getToolByName(self, 'portal_workflow')
    
    ourProductWorkflow = ExternalMethod('temp',
                         'temp',
                         productname+'.'+'poi_tracker_workflow',
                         'createpoi_tracker_workflow')
    workflow = ourProductWorkflow(self, 'poi_tracker_workflow')
    workflowTool._setObject('poi_tracker_workflow', workflow)
    workflowTool.setChainForPortalTypes(['PoiTracker'], workflow.getId())
    ourProductWorkflow = ExternalMethod('temp',
                         'temp',
                         productname+'.'+'poi_issue_workflow',
                         'createpoi_issue_workflow')
    workflow = ourProductWorkflow(self, 'poi_issue_workflow')
    workflowTool._setObject('poi_issue_workflow', workflow)
    workflowTool.setChainForPortalTypes(['PoiIssue'], workflow.getId())
    
    return workflowTool
