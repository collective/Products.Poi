#
# Initialise the product's module. There are three ways to inject custom code
# here:
#
#   - To set global configuration variables, create a file AppConfig.py. This
#       will be imported in config.py, which in turn is imported in each
#       generated class and in this file.
#   - To perform custom initialisation after types have been registered, use
#       the protected code section at the bottom of initialize().
#   - To register a customisation policy, create a file CustomizationPolicy.py
#       with a method register(context) to register the policy
#

from zLOG import LOG, INFO

LOG('Poi',INFO, 'Installing Product')

try:
    import CustomizationPolicy
except ImportError:
    CustomizationPolicy=None

from Globals import package_home
from Products.CMFCore import utils, CMFCorePermissions, DirectoryView
from Products.CMFPlone.PloneUtilities import ToolInit
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path

from Products.Poi.config import *

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/Poi',
                                    product_globals)

##code-section custom-init-head #fill in your manual code here
##/code-section custom-init-head


def initialize(context):
    ##code-section custom-init-top #fill in your manual code here
    ##/code-section custom-init-top

    # imports packages and types for registration
    import interfaces
    import psc

    import PoiTracker
    import PoiIssue
    import PoiResponse
    import Tracker

    # initialize portal content
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    # apply customization-policy, if theres any
    if CustomizationPolicy and hasattr(CustomizationPolicy, 'register'):
        CustomizationPolicy.register(context)
        print 'Customization policy for Poi installed'

    ##code-section custom-init-bottom #fill in your manual code here
    
    # Set up some manual add permissions

    import Permissions
        
    # Issues
    for metaType, constructor in \
        {'PoiIssue' : PoiIssue.addPoiIssue,
         'PoiPscIssue' : psc.PoiPscIssue.addPoiPscIssue}.items ():
        context.registerClass(meta_type    = metaType,
                              constructors = (constructor,),
                              permission   = Permissions.AddIssue)
    
    # Responses
    for metaType, constructor in \
        {'PoiResponse'    : PoiResponse.addPoiResponse,}.items ():
        context.registerClass(meta_type    = metaType,
                              constructors = (constructor,),
                              permission   = Permissions.AddResponse)

    
                 
    ##/code-section custom-init-bottom

