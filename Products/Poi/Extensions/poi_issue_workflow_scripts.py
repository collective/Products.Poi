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


# Workflow Scripts for: poi_issue_workflow

from Products.CMFCore.utils import getToolByName


def sendInitialEmail(self, state_change, **kw):
    state_change.object.sendNotificationMail()


def sendResolvedMail(self, state_change, **kw):
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

    memberInfo = portal_membership.getMemberInfo(member.getUserName())
    stateChanger = member.getUserName()
    if memberInfo:
        stateChanger = memberInfo['fullname'] or stateChanger

    portal_url = getToolByName(self, 'portal_url')
    portal = portal_url.getPortalObject()
    fromName = portal.getProperty('email_from_name', None)
    mailText = issue.poi_email_issue_resolved(issue,
                                              tracker = tracker,
                                              issue = issue,
                                              fromName = fromName,
                                              stateChanger = stateChanger)
    subject = "[%s] Resolved #%s - %s" % (
        tracker.getExternalTitle(), issue.getId(), issue.Title())

    tracker.sendNotificationEmail([issueEmail], subject, mailText)
