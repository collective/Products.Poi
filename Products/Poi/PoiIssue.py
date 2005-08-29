# File: PoiIssue.py
# 
# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.4.0-beta2 devel 
#            http://plone.org/products/archgenxml
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
__author__  = '''Martin Aspeli <optilude@gmx.net>'''
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *

from Products.Poi.interfaces.Issue import Issue
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder


# additional imports from tagged value 'import'
import Permissions
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import log_exc
##/code-section module-header

schema=Schema((
    StringField('id',
        widget=StringWidget(
            visible={'view' : 'invisible', 'edit': 'visible'},
            modes=('view',),
            label='Id',
            label_msgid='Poi_label_id',
            description_msgid='Poi_help_id',
            i18n_domain='Poi',
        ),
        mode="r"
    ),
    
    StringField('title',
        widget=StringWidget(
            label="Title",
            description="Enter a short, descriptive title for the issue. A good title will make it easier for project managers to identify and respond to the issue.",
            label_msgid='Poi_label_title',
            description_msgid='Poi_help_title',
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title",
        searchable=True
    ),
    
    TextField('description',
        widget=TextAreaWidget(
            label="Overview",
            description="Enter a brief overview of the issue. As with the title, a consise, meaningful description will make it easier for project managers to assess and respond to the issue.",
            label_msgid='Poi_label_description',
            description_msgid='Poi_help_description',
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Description",
        searchable=True
    ),
    
    StringField('release',
        default="(UNASSIGNED)",
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Release",
            description="Select the release this issue pertains to.",
            condition="object/isUsingReleases",
            label_msgid='Poi_label_release',
            description_msgid='Poi_help_release',
            i18n_domain='Poi',
        ),
        required=True,
        vocabulary='getReleasesVocab'
    ),
    
    StringField('topic',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Topic",
            description="Select the topic this issue is relevant to.",
            label_msgid='Poi_label_topic',
            description_msgid='Poi_help_topic',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        vocabulary='getTopicsVocab',
        required=True
    ),
    
    StringField('category',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Category",
            description="Select the category this issue corresponds to.",
            label_msgid='Poi_label_category',
            description_msgid='Poi_help_category',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        vocabulary='getCategoriesVocab',
        required=True
    ),
    
    StringField('severity',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Severity",
            description="Select the severity of this issue.",
            label_msgid='Poi_label_severity',
            description_msgid='Poi_help_severity',
            i18n_domain='Poi',
        ),
        vocabulary='getAvailableSeverities',
        default_method='getDefaultSeverity',
        required=True,
        write_permission=Permissions.ModifySeverity
    ),
    
    TextField('details',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label="Details",
            description="Please provide further details",
            rows="""6
            python:('text/structured', 'text/plain', 'text/html', 'text/restructured')""",
            label_msgid='Poi_label_details',
            description_msgid='Poi_help_details',
            i18n_domain='Poi',
        ),
        required=False,
        default_content_type="text/structured",
        searchable=True,
        default_output_type="text/html"
    ),
    
    LinesField('steps',
        widget=LinesWidget(
            label="Steps to reproduce",
            description="If applicable, please provide the steps to reproduce the error or identify the issue, one per line.",
            label_msgid='Poi_label_steps',
            description_msgid='Poi_help_steps',
            i18n_domain='Poi',
        ),
        searchable=True
    ),
    
    FileField('attachment',
        widget=FileWidget(
            label="Attachment",
            description="You may optionally upload a file attachment to your issue. Please do not upload unnecessarily large files.",
            label_msgid='Poi_label_attachment',
            description_msgid='Poi_help_attachment',
            i18n_domain='Poi',
        ),
        storage=AttributeStorage()
    ),
    
    StringField('contactEmail',
        validators=('isEmail',),
        widget=StringWidget(
            label="Contact email address",
            description="Optionally, provide an email address where you can be contacted for further information or when a resolution is available.",
            label_msgid='Poi_label_contactEmail',
            description_msgid='Poi_help_contactEmail',
            i18n_domain='Poi',
        ),
        required=True,
        default_method="getDefaultContactEmail"
    ),
    
    StringField('responsibleManager',
        index="FieldIndex:schema",
        widget=SelectionWidget(
            label="Responsible",
            description="Select which manager, if any, is responsible for this issue.",
            label_msgid='Poi_label_responsibleManager',
            description_msgid='Poi_help_responsibleManager',
            i18n_domain='Poi',
        ),
        vocabulary='getManagersVocab',
        default="(UNASSIGNED)",
        required=True,
        write_permission=Permissions.ModifyIssueAssignment
    ),
    
),
)


##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiIssue(BrowserDefaultMixin,BaseFolder):
    """
    The default tracker
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BrowserDefaultMixin,'__implements__',()),) + (getattr(BaseFolder,'__implements__',()),) + (Issue,INonStructuralFolder,)


    # This name appears in the 'add' box
    archetype_name             = 'Issue'

    meta_type                  = 'PoiIssue' 
    portal_type                = 'PoiIssue' 
    allowed_content_types      = ['PoiResponse'] 
    filter_content_types       = 1
    global_allow               = 0
    allow_discussion           = 0
    content_icon               = 'PoiIssue.gif'
    immediate_view             = 'base_view'
    default_view               = 'poi_issue_view'
    suppl_views                = ()
    typeDescription            = "An issue. Issues begin in the 'open' state, and can be responded to by project mangers."
    typeDescMsgId              = 'description_edit_poiissue'

    actions =  (


       {'action':      "string:${object_url}/view",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': (Permissions.View,),
        'condition'  : 'python:1'
       },
        

       {'action':      "string:${object_url}/edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': (Permissions.ModifyPortalContent,),
        'condition'  : 'python:1'
       },
        

    )

    _at_rename_after_creation  = True 

    schema = BaseFolderSchema + \
             schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

    security.declareProtected(Permissions.View, 'getCurrentIssueState')
    def getCurrentIssueState(self):
        """
        Get the current state of the issue.
        
        Used by PoiResponse to select a default for the new issue
        state selector.
        """

        wftool = getToolByName(self, 'portal_workflow')
        return wftool.getInfoFor(self, 'review_state')



    security.declareProtected(Permissions.View, 'getAvailableIssueTransitions')
    def getAvailableIssueTransitions(self):
        """
        Get the available transitions for the issue.
        """

        wftool = getToolByName(self, 'portal_workflow')
        transitions = DisplayList()
        transitions.add('', 'No change')
        for tdef in wftool.getTransitionsFor(self):
            transitions.add(tdef['id'], tdef['title_or_id'])
        return transitions


    #manually created methods

    def getDefaultContactEmail(self):
        """Get the default email address, that of the creating user"""
        portal_membership = getToolByName(self, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        email = member.getProperty('email', '')
        return email


    def _renameAfterCreation(self, check_auto_id=False):
        parent = self.aq_inner.aq_parent
        maxId = 0
        for id in parent.objectIds():
            try:
                intId = int(id)
                maxId = max(maxId, intId)
            except (TypeError, ValueError):
                pass
        newId = str(maxId + 1)
        # Can't rename without a subtransaction commit when using
        # portal_factory!
        get_transaction().commit(1)
        self.setId(newId)

        # Send notification email
        self.sendNotificationMail()


    def getDefaultSeverity(self):
        """Get the default severity for new issues"""
        return self.aq_parent.getDefaultSeverity()


    security.declarePublic('isValid')
    def isValid(self):
        """Check if the response is valid, that is, a response has been filled in"""
        errors = {}
        self.Schema().validate(self, None, errors, 1, 1)
        if errors:
            return False
        else:
            return True


    security.declarePublic('getTopicsVocab')
    def getTopicsVocab(self):
        """
        Get the available topics as a DispayList.
        """
        field = self.aq_parent.getField('availableTopics')
        return field.getAsDisplayList(self.aq_parent)


    def SearchableText(self):
        """Include in the SearchableText the text of all responses"""
        text = BaseObject.SearchableText(self)
        responses = self.contentValues('PoiResponse')
        text += ' ' + ' '.join([r.SearchableText() for r in responses])
        return text


    def getReleasesVocab(self):
        """
        Get the vocabulary of available releases, including the item
        (UNASSIGNED) to denote that a release is not yet assigned.
        """
        vocab = DisplayList()
        vocab.add('(UNASSIGNED)', 'None', 'poi_voacb_none')
        parentVocab = self.aq_parent.getReleasesVocab()
        for k in parentVocab.keys():
            vocab.add(k, parentVocab.getValue(k), parentVocab.getMsgId(k))
        return vocab


    def getManagersVocab(self):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.
        """
        items = self.aq_parent.getManagers()
        vocab = DisplayList()
        vocab.add('(UNASSIGNED)', 'None', 'poi_voacb_none')
        for item in items:
            vocab.add(item, item)
        return vocab


    def getCategoriesVocab(self):
        """
        Get the categories available as a DisplayList.
        """
        field = self.aq_parent.getField('availableCategories')
        return field.getAsDisplayList(self.aq_parent)


    def sendNotificationMail(self):
        """When this issue is created, send a notification email to all
        tracker managers, unless emailing is turned off.
        """
        tracker = self.aq_parent

        if not tracker.getSendNotificationEmails():
            return

        portal_membership = getToolByName(self, 'portal_membership')
        portal_url        = getToolByName(self, 'portal_url')
        plone_utils       = getToolByName(self, 'plone_utils')

        portal = portal_url.getPortalObject()
        mailHost = plone_utils.getMailHost()
        fromAddress = portal.getProperty('email_from_address', None)
        fromName = portal.getProperty('email_from_name', None)

        if fromAddress is None or fromName is None:
            return None

        mailText = self.poi_notify_new_issue(self, issue = self, fromName = fromName)

        mailingList = self.getMailingList()

        if mailingList:
            try:
                mailHost.secureSend(message = mailText,
                                    mto = mailingList,
                                    mfrom = fromAddress,
                                    subject = "New issue in tracker '%s'" % tracker.Title(),
                                    subtype = 'html')
            except ConflictError:
                raise
            except:
                log_exc('Could not send email from %s to %s regarding creation of issue %s.' % (fromAddress, mailingList, self.absolute_url(),))
                pass
        else:
            managers = self.getManagers()
            for manager in managers:
                managerUser = portal_membership.getMemberById(manager)
                if managerUser is not None:
                    managerEmail = managerUser.getProperty('email')
                    if managerEmail:
                        try:
                            mailHost.secureSend(message = mailText,
                                                mto = managerEmail,
                                                mfrom = fromAddress,
                                                subject = "New issue in tracker '%s'" % tracker.Title(),
                                                subtype = 'html')
                        except ConflictError:
                            raise
                        except:
                            log_exc('Could not send email from %s to %s regarding creation of issue %s.' % (fromAddress, managerEmail, self.absolute_url(),))
                            pass

    def updateResponses(self):
        """When a response is added or modified, this method should be
        called to ensure responses are correctly indexed.
        """
        self.reindexObject(('SearchableText'))

def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiIssue,PROJECTNAME)
# end of class PoiIssue

##code-section module-footer #fill in your manual code here
##/code-section module-footer



