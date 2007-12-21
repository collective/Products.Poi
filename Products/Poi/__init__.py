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


# There are three ways to inject custom code here:
#
#   - To set global configuration variables, create a file AppConfig.py.
#       This will be imported in config.py, which in turn is imported in
#       each generated class and in this file.
#   - To perform custom initialisation after types have been registered,
#       use the protected code section at the bottom of initialize().
#   - To register a customisation policy, create a file CustomizationPolicy.py
#       with a method register(context) to register the policy.

from zLOG import LOG, DEBUG

LOG('Poi', DEBUG, 'Installing Product')

try:
    import CustomizationPolicy
except ImportError:
    CustomizationPolicy = None

from Products.CMFCore import utils as cmfutils

try: # New CMF 
    from Products.CMFCore import permissions as CMFCorePermissions
except: # Old CMF 
    from Products.CMFCore import CMFCorePermissions

from Products.CMFCore import DirectoryView
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes

from Products.Poi.config import *

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/Poi',
                                    product_globals)

##code-section custom-init-head #fill in your manual code here

# This code *has* to be run before PoiTracker is imported as it uses
# this validator.  That means for instance that putting it in the
# initialize method is too late as content.PoiTracker is already
# imported when loading the configure.zcml.
# We could put it in PoiTracker.py itself but I don't like that.
# This is a candidate for putting in DataGridField.
from Products.validation import validation
from Products.Poi.validators import AtLeastOneValidator
validation.register(AtLeastOneValidator('atLeastOne'))
##/code-section custom-init-head


def initialize(context):
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    import interfaces
    import psc
    import content


    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0,len(all_content_types)):
        klassname=all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])

    # Apply customization-policy, if theres any
    if CustomizationPolicy and hasattr(CustomizationPolicy, 'register'):
        CustomizationPolicy.register(context)
        print 'Customization policy for Poi installed'

    ##code-section custom-init-bottom #fill in your manual code here
    ##/code-section custom-init-bottom

