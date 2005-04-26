from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

def installWorkflows(self,package,out):
    ''' '''
    productname='Poi'
    wft=getToolByName(self,'portal_workflow')

                
    iwf=ExternalMethod('temp','temp',productname+'.'+'poi_tracker_workflow', 'createpoi_tracker_workflow') 
    wf=iwf(self,'poi_tracker_workflow')
    wft._setObject('poi_tracker_workflow',wf)
    wft.setChainForPortalTypes( ['PoiTracker'],wf.getId())
    
                    
    iwf=ExternalMethod('temp','temp',productname+'.'+'poi_issue_workflow', 'createpoi_issue_workflow') 
    wf=iwf(self,'poi_issue_workflow')
    wft._setObject('poi_issue_workflow',wf)
    wft.setChainForPortalTypes( ['PoiIssue'],wf.getId())
    
            
    
    return wft
