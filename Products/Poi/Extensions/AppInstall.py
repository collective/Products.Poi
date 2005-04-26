from Products.CMFCore.utils import getToolByName
from StringIO import StringIO

def addCatalogMetadata(self, out, catalog, column):
    """Add the given column to the catalog's metadata schema"""
    if column not in catalog.schema():
        catalog.addColumn(column)
        print >> out, "Added", column, "to catalog metadata"
    else:
        print >> out, column, "already in catalog metadata"

def install(self):
    
    out = StringIO()
    
    # Add additional workflow mapings
    wftool = getToolByName(self, 'portal_workflow')
    wftool.setChainForPortalTypes(['PoiPscTracker'], 'poi_tracker_workflow')
    wftool.setChainForPortalTypes(['PoiPscIssue'], 'poi_issue_workflow')
    wftool.setChainForPortalTypes(['PoiResponse', 'PoiPscResponse'], '')
    
    print >> out, "Set additional workflows for types"
    
    # Add UID to catalog metadata
    catalog = getToolByName(self, 'portal_catalog')
    addCatalogMetadata(self, out, catalog, 'UID')
    
    print >> out, "Added UID to catalog metadata"
    
    return out.getvalue()