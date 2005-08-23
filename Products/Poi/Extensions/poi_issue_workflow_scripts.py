""" Workflow Scripts for: poi_issue_workflow """

# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
#
# Generator: ArchGenXML Version 1.4.0-beta1 devel
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

    portal_membership = getToolByName(issue, 'portal_membership')
    portal_url        = getToolByName(issue, 'portal_url')
    plone_utils       = getToolByName(issue, 'plone_utils')

    portal = portal_url.getPortalObject()
    mailHost = plone_utils.getMailHost()
    fromAddress = portal.getProperty('email_from_address', None)
    fromName = portal.getProperty('email_from_name', None)

    if fromAddress is None or fromName is None:
        return

    mailText = issue.poi_notify_issue_resolved(issue, issue = issue, fromName = fromName)
    try:
        mailHost.secureSend(message = mailText,
                            mto = issueEmail,
                            mfrom = fromAddress,
                            subject = "Issue '%s' in tracker '%s' resolved" % (issue.Title(), tracker.Title(),),
                            subtype = 'html')
    except ConflictError:
        raise
    except:
        log_exc('Could not send email from %s to %s regarding resolution of issue %s.' % (fromAddress, issueEmail, issue.absolute_url(),))
        pass


