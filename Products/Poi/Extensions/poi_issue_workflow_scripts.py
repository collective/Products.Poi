""" Workflow Scripts for: poi_issue_workflow """

# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
#
# Generator: ArchGenXML Version 1.4.0-RC2 svn/development
#            http://sf.net/projects/archetypes/
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
__author__    = '''Martin Aspeli <optilude@gmx.net>'''
__docformat__ = 'plaintext'
__version__   = '$ Revision 0.0 $'[11:-2]

##code-section workflow-script-header #fill in your manual code here
from ZODB.POSException import ConflictError
from Products.CMFPlone.utils import log_exc
from Products.CMFCore.utils import getToolByName
##/code-section workflow-script-header

## ['sendResolvedMail']

def sendResolvedMail(self,state_change,**kw):
    """Send an email to the original submitter that the issue was marked
    as resolved, inviting him/her to confirm it.
    """
    issue = state_change.object
    tracker = issue.aq_parent
    
    if not tracker.getSendNotificationEmails():
        return

    issueEmail = issue.getContactEmail()
    if not issueEmail:
        return

    portal_membership = getToolByName(self, 'portal_membership')
    member = portal_membership.getAuthenticatedMember()

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()
    fromName = portal.getProperty('email_from_name', None)
    mailText = issue.poi_notify_issue_resolved(issue, issue = issue, fromName = fromName, stateChanger = member.getUserName())
    subject = "[%s] Issue '%s. %s' resolved" % (tracker.Title(), issue.getId(), issue.Title(),)

    tracker.sendNotificationEmail([issueEmail], subject, mailText)


