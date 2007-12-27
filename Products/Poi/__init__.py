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

from zLOG import LOG, DEBUG

LOG('Poi', DEBUG, 'Installing Product')

from Products.CMFCore import utils as cmfutils

from Products.CMFCore import permissions as CMFCorePermissions

from Products.CMFCore import DirectoryView
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes

from Products.Poi.config import *

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/Poi',
                                    product_globals)

##code-section custom-init-head #fill in your manual code here

# This code *has* to be run before PoiTracker is imported as it uses
# the validator we are registering here by importing a module.  That
# means for instance that putting it in the initialize method is too
# late as content.PoiTracker is already imported when loading the
# configure.zcml.

# The Poi validator was copied to DataGridField 1.6 beta 3 so it may
# already be registered.  In that case we do not care which of the two
# validators is used.  The plan is to remove the validator from Poi
# when DataGridField 1.6 is widely available.  No imports here are
# needed in that case as DataGridField then takes care of that.

from Products.validation.exceptions import AlreadyRegisteredValidatorError
try:
    from Products.Poi import validators
except AlreadyRegisteredValidatorError:
    # This is never actually raised except in commented out code, but
    # let's be careful and catch this exception.
    pass

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

    ##code-section custom-init-bottom #fill in your manual code here
    ##/code-section custom-init-bottom

