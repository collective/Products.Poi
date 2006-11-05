# -*- coding: utf-8 -*-
#
# File: Poi.py
#
# Copyright (c) 2006 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.5.1-svn
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


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. This will be included
# in this file if found.

from Products.CMFCore.CMFCorePermissions import setDefaultRoles
##code-section config-head #fill in your manual code here
##/code-section config-head


PROJECTNAME = "Poi"

# Check for Plone 2.1
try:
    from Products.CMFPlone.migrations import v2_1
except ImportError:
    HAS_PLONE21 = False
else:
    HAS_PLONE21 = True

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'PoiTracker': 'Poi: Add Tracker',
    'PoiIssue': 'Poi: Add Issue',
    'PoiResponse': 'Poi: Add Response',
}

setDefaultRoles('Poi: Add Tracker', ('Manager',))
setDefaultRoles('Poi: Add Issue', ('Anonymous', 'Manager', 'Member', 'Owner',))
setDefaultRoles('Poi: Add Response', ('Anonymous', 'Manager', 'Member', 'Owner',))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

# You can overwrite these two in an AppConfig.py:
# STYLESHEETS = [{'id': 'my_global_stylesheet.css'},
#                {'id': 'my_contenttype.css',
#                 'expression': 'python:object.getTypeInfo().getId() == "MyType"'}]
# You can do the same with JAVASCRIPTS.
STYLESHEETS = []
JAVASCRIPTS = []

##code-section config-bottom #fill in your manual code here
DEPENDENCIES = ['DataGridField', 'AddRemoveWidget', 'intelligenttext']
DESCRIPTION_LENGTH = 200
RUN_MIGRATIONS = True
PSC_TRACKER_ID = 'issues'

#
# Support for plain-text/rich-text
#

# Add text/html to the list of mimetypes to allow HTML/kupu issue/response text.
ISSUE_MIME_TYPES = ('text/x-web-intelligent',)
DEFAULT_ISSUE_MIME_TYPE = 'text/x-web-intelligent'

##/code-section config-bottom


# Load custom configuration not managed by ArchGenXML
try:
    from Products.Poi.AppConfig import *
except ImportError:
    pass
