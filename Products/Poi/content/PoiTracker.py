# File: PoiTracker.py
# 
# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.4.1 svn/devel 
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
from Products.Poi.interfaces.Tracker import Tracker
from Products.CMFPlone.interfaces.NonStructuralFolder import INonStructuralFolder


# additional imports from tagged value 'import'
from Products.DataGridField.DataGridField import DataGridField
from Products.Poi import permissions
from Products.DataGridField.DataGridWidget import DataGridWidget
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.Poi.config import *
##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import log_exc, log
from ZTUtils import make_query

from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.Message import Message
import sets
##/code-section module-header

schema=Schema((
    StringField('title',
        widget=StringWidget(
            label="Tracker name",
            description="Enter a descriptive name for this tracker",
            label_msgid="Poi_label_tracker_title",
            description_msgid="Poi_help_tracker_title",
            i18n_domain='Poi',
        ),
        required=True,
        accessor="Title"
    ),

    TextField('description',
        widget=TextAreaWidget(
            label="Tracker description",
            description="Describe the purpose of this tracker",
            label_msgid='Poi_label_description',
            description_msgid='Poi_help_description',
            i18n_domain='Poi',
        ),
        use_portal_factory="1",
        accessor="Description",
        searchable=True
    ),

    DataGridField('availableAreas',
        default=({'id' : 'ui', 'title' : 'User interface', 'description' : 'User interface issues'}, {'id' : 'functionality', 'title' : 'Functionality', 'description' : 'Issues with the basic functionality'}, {'id' : 'process', 'title' : 'Process', 'description' : 'Issues relating to the development process itself'}),
        widget=DataGridWidget(
            label="Areas",
            description="Enter the issue topics/areas for this tracker.",
            column_names=('Short name', 'Title', 'Description',),
            label_msgid='Poi_label_availableAreas',
            description_msgid='Poi_help_availableAreas',
            i18n_domain='Poi',
        ),
        required=True,
        columns=('id', 'title', 'description',)
    ),

    DataGridField('availableIssueTypes',
        default=({'id' : 'bug', 'title' : 'Bug', 'description' : 'Functionality bugs in the software'}, {'id' : 'feature', 'title' : 'Feature', 'description' : 'Suggested features'}, {'id' : 'patch', 'title' : 'Patch', 'description' : 'Patches to the software'}),
        widget=DataGridWidget(
            label="Issue types",
            description="Enter the issue types for this tracker.",
            column_names=('Short name', 'Title', 'Description',),
            label_msgid='Poi_label_availableIssueTypes',
            description_msgid='Poi_help_availableIssueTypes',
            i18n_domain='Poi',
        ),
        required=True,
        columns=('id', 'title', 'description')
    ),

    LinesField('availableSeverities',
        default=['Critical', 'Important', 'Medium', 'Low'],
        widget=LinesWidget(
            label="Available severities",
            description="Enter the different type of issue severities that should be available, one per line.",
            label_msgid='Poi_label_availableSeverities',
            description_msgid='Poi_help_availableSeverities',
            i18n_domain='Poi',
        ),
        required=True
    ),

    StringField('defaultSeverity',
        default='Medium',
        widget=SelectionWidget(
            label="Default severity",
            description="Select the default severity for new issues.",
            label_msgid='Poi_label_defaultSeverity',
            description_msgid='Poi_help_defaultSeverity',
            i18n_domain='Poi',
        ),
        enforceVocabulary=True,
        vocabulary='getAvailableSeverities',
        required=True
    ),

    LinesField('availableReleases',
        widget=LinesWidget(
            label="Available releases",
            description="Enter the releases which issues can be assigned to, one per line. If no releases are entered, issues will not be organised by release.",
            label_msgid='Poi_label_availableReleases',
            description_msgid='Poi_help_availableReleases',
            i18n_domain='Poi',
        ),
        required=False
    ),

    LinesField('managers',
        widget=LinesWidget(
            label="Tracker managers",
            description="Enter the user ids of the users who will be allowed to manage this tracker, one per line.",
            label_msgid='Poi_label_managers',
            description_msgid='Poi_help_managers',
            i18n_domain='Poi',
        ),
        default_method="getDefaultManagers"
    ),

    BooleanField('sendNotificationEmails',
        default=True,
        widget=BooleanWidget(
            label="Send notification emails",
            description="If selected, tracker managers will receive an email each time a new issue or response is posted, and issue submitters will receive an email when there is a new response and when an issue has been resolved, awaiting confirmation.",
            label_msgid='Poi_label_sendNotificationEmails',
            description_msgid='Poi_help_sendNotificationEmails',
            i18n_domain='Poi',
        )
    ),

    StringField('mailingList',
        widget=StringWidget(
            label="Mailing list",
            description="""If given, and if "Send notification emails" is selected, an email will be sent to this address each time a new issue or response is posted. If no mailing list address is given, managers will receive individual emails.""",
            label_msgid='Poi_label_mailingList',
            description_msgid='Poi_help_mailingList',
            i18n_domain='Poi',
        ),
        required=False,
        validators=('isEmail',)
    ),

),
)


##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PoiTracker_schema = BaseBTreeFolderSchema + \
    schema

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PoiTracker(BrowserDefaultMixin,BaseBTreeFolder):
    """
    The default tracker
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BrowserDefaultMixin,'__implements__',()),) + (getattr(BaseBTreeFolder,'__implements__',()),) + (Tracker,INonStructuralFolder,)


    # This name appears in the 'add' box
    archetype_name             = 'Issue Tracker'

    meta_type                  = 'PoiTracker'
    portal_type                = 'PoiTracker'
    allowed_content_types      = ['PoiIssue']
    filter_content_types       = 1
    global_allow               = 1
    allow_discussion           = 0
    content_icon               = 'PoiTracker.gif'
    immediate_view             = 'base_view'
    default_view               = 'poi_tracker_view'
    suppl_views                = ()
    typeDescription            = "An issue tracker"
    typeDescMsgId              = 'description_edit_poitracker'

    actions =  (


       {'action':      "string:${object_url}",
        'category':    "object",
        'id':          'view',
        'name':        'View',
        'permissions': (permissions.View,),
        'condition'  : 'python:1'
       },


       {'action':      "string:${object_url}/edit",
        'category':    "object",
        'id':          'edit',
        'name':        'Edit',
        'permissions': (permissions.ModifyPortalContent,),
        'condition'  : 'python:1'
       },


    )

    _at_rename_after_creation  = True

    schema = PoiTracker_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header


    #Methods

    security.declareProtected(permissions.View, 'getFilteredIssues')
    def getFilteredIssues(self, criteria=None, **kwargs):
        """
        Get the contained issues in the given criteria.
        """
        catalog = getToolByName(self, 'portal_catalog')
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        return catalog.searchResults(query)



    security.declareProtected(permissions.View, 'isUsingReleases')
    def isUsingReleases(self):
        """Return a boolean indicating whether this tracker is using releases.
        """
        return len(self.getAvailableReleases()) > 0



    security.declareProtected(permissions.View, 'getReleasesVocab')
    def getReleasesVocab(self):
        """
        Get the releases available to the tracker as a DisplayList.
        """
        items = self.getAvailableReleases()
        vocab = DisplayList()
        for item in items:
            vocab.add(item, item)
        return vocab


    security.declarePrivate('_getMemberEmail')
    def _getMemberEmail(self, username, portal_membership=None):
        """Query portal_membership to figure out the specified email address
        for the given user (via the username parameter) or return None if none
        is present.
        """
        
        if portal_membership is None:
            portal_membership = getToolByName(self, 'portal_membership')
            
        member = portal_membership.getMemberById(username)
        if member is None:
            return None
        
        return member.getProperty('email')


    security.declarePrivate('getNotificationEmailAddresses')
    def getNotificationEmailAddresses(self, issue=None):
        """
        Upon activity for the given issue, get the list of email
        addresses to which notifications should be sent. May return an 
        empty list if notification is turned off. If issue is given, the 
        issue poster and any watchers will also be included.
        """

        if not self.getSendNotificationEmails():
            return []
        
        portal_membership = getToolByName(self, 'portal_membership')
        
        member = portal_membership.getAuthenticatedMember()
        email = member.getProperty('email')
        
        # make sure no duplicates are added
        addresses = sets.Set()
        
        mailingList = self.getMailingList()
        if mailingList:
            addresses.add(mailingList)
        else:
            addresses.union_update([self._getMemberEmail(x, portal_membership) 
                                    for x in self.getManagers() or []])
        
        if issue is not None:
            addresses.add(issue.getContactEmail())
            addresses.union_update([self._getMemberEmail(x, portal_membership)
                                    for x in issue.getWatchers() or []])

        addresses.discard(None)
        addresses.discard(email)

        return tuple(addresses)
        


    security.declarePrivate('sendNotificationEmail')
    def sendNotificationEmail(self, addresses, subject, text, subtype='html'):
        """
        Send a notification email to the list of addresses
        """
        
        if not self.getSendNotificationEmails() or not addresses:
            return
        
        portal_url  = getToolByName(self, 'portal_url')
        plone_utils = getToolByName(self, 'plone_utils')

        portal      = portal_url.getPortalObject()
        mailHost    = plone_utils.getMailHost()
        charset     = plone_utils.getSiteEncoding()
        fromAddress = portal.getProperty('email_from_address', None)
        
        if fromAddress is None:
            log('Cannot send notification email: email sender address or name not set')
            return
        
        if subtype == 'html':
            transformTool = getToolByName(self, 'portal_transforms')
            plainText = str(transformTool.convertTo('text/plain', text)).strip()
            
            message = MIMEMultipart('alternative')
            message.epilogue = ''
            
            textPart = MIMEText(plainText, 'plain', charset)
            message.attach(textPart)
            htmlPart = MIMEText(text, 'html', charset)
            message.attach(htmlPart)
        else:
            message = text
        
        if isinstance(message, Message):
            message = str(message)
        
        for address in addresses:
            try:
                mailHost.send(message = message,
                              mto = address,
                              mfrom = fromAddress,
                              subject = subject)
            except ConflictError:
                raise
            except:
                log_exc('Could not send email from %s to %s regarding issue in tracker %s\ntext is:\n%s\n' % (fromAddress, address, self.absolute_url(), text,))



    security.declareProtected(permissions.View, 'getTagsInUse')
    def getTagsInUse(self):
        """
        Get a list of the issue tags in use in this tracker.
        """
        catalog = getToolByName(self, 'portal_catalog')
        issues = catalog.searchResults(portal_type = 'PoiIssue',
                                       path = '/'.join(self.getPhysicalPath()))
        tags = {}
        for i in issues:
            for s in i.Subject:
                tags[s] = 1
        keys = tags.keys()
        keys.sort(lambda x, y: cmp(x.lower(), y.lower()))
        return keys
        


    security.declareProtected(permissions.View, 'getExternalTitle')
    def getExternalTitle(self):
        """
        Get the external title of this tracker.
        This will be the name used in outgoing emails, for example.
        """
        return self.Title()


    #manually created methods

    def canSelectDefaultPage(self):
        """Explicitly disallow selection of a default-page."""
        return False


    security.declareProtected(permissions.View, 'getIssueSearchQueryString')
    def getIssueSearchQueryString(self, criteria=None, **kwargs):
        """
        Return a query string (name=value&name=value etc.) for an issue
        query.
        """
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        return make_query(query)                


    security.declareProtected(permissions.ModifyPortalContent, 'setManagers')
    def setManagers(self, managers):
        """
        Set the list of tracker managers, and give them the Manager local role.
        """
        field = self.getField('managers')
        currentManagers = field.get(self)
        field.set(self, managers)

        toRemove = [m for m in currentManagers if m not in managers]
        toAdd = [m for m in managers if m not in currentManagers]
        if toRemove:
            self.manage_delLocalRoles(toRemove)
        for userId in toAdd:
            self.manage_setLocalRoles(userId, ['Manager'])


    security.declarePublic('getIssueWorkflowStates')
    def getIssueWorkflowStates(self):
        """Get a DisplayList of the workflow states available on issues"""
        portal_workflow = getToolByName(self, 'portal_workflow')
        chain = portal_workflow.getChainForPortalType('PoiIssue')
        workflow = getattr(portal_workflow, chain[0])
        states = getattr(workflow, 'states')
        vocab = DisplayList()
        for id, state in states.items():
            vocab.add(id, state.title)
        return vocab.sortedByValue()


    def validate_managers(self, value):
        """Make sure issue tracker managers are actual user ids"""
        membership = getToolByName(self, 'portal_membership')
        notFound = []
        for userId in value:
            member = membership.getMemberById(userId)
            if member is None:
                notFound.append(userId)
        if notFound:
            return "The following user ids could not be found: %s" % ','.join(notFound)
        else:
            return None


    def getDefaultManagers(self):
        """The default list of managers should include the tracker owner"""
        return (self.Creator(),)


    def buildIssueSearchQuery(self, criteria=None, **kwargs):
        """
        Build canoical query for issue search
        """

        if criteria is None:
            criteria = kwargs

        allowedCriteria = {'release'       : 'getRelease',
                           'area'          : 'getArea',
                           'issueType'     : 'getIssueType',
                           'severity'      : 'getSeverity',
                           'targetRelease' : 'getTargetRelease',
                           'state'         : 'review_state',
                           'tags'          : 'Subject',
                           'responsible'   : 'getResponsibleManager',
                           'creator'       : 'Creator',
                           'text'          : 'SearchableText',
                           'id'            : 'getId',
                           }

        query                = {}
        query['path']        = '/'.join(self.getPhysicalPath())
        query['portal_type'] = ['PoiIssue']

        for k, v in allowedCriteria.items():
            if k in criteria:
                query[v] = criteria[k]
            elif v in criteria:
                query[v] = criteria[v]

        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')

        return query


def modify_fti(fti):
    # hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(PoiTracker,PROJECTNAME)
# end of class PoiTracker

##code-section module-footer #fill in your manual code here
##/code-section module-footer



