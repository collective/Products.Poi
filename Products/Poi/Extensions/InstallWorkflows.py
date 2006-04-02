# File: Poi.py
#
# Copyright (c) 2006 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.4.1 svn/devel
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
from Products.ExternalMethod.ExternalMethod import ExternalMethod

def installWorkflows(self, package, out):
    """Install the custom workflows for this product."""

    productname = 'Poi'
    workflowTool = getToolByName(self, 'portal_workflow')

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                         productname+'.'+'poi_tracker_workflow',
                         'createpoi_tracker_workflow')
    workflow = ourProductWorkflow(self, 'poi_tracker_workflow')
    workflowTool._setObject('poi_tracker_workflow', workflow)
    workflowTool.setChainForPortalTypes(['PoiTracker', 'PoiPscTracker'], workflow.getId())

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                         productname+'.'+'poi_issue_workflow',
                         'createpoi_issue_workflow')
    workflow = ourProductWorkflow(self, 'poi_issue_workflow')
    workflowTool._setObject('poi_issue_workflow', workflow)
    workflowTool.setChainForPortalTypes(['PoiIssue'], workflow.getId())

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                         productname+'.'+'poi_response_workflow',
                         'createpoi_response_workflow')
    workflow = ourProductWorkflow(self, 'poi_response_workflow')
    workflowTool._setObject('poi_response_workflow', workflow)
    workflowTool.setChainForPortalTypes(['PoiResponse'], workflow.getId())

    return workflowTool
