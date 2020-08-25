# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.app.textfield import RichTextValue
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Poi.adapters import IResponseContainer
from Products.Poi.content.issue import next_issue_id
from Products.Poi.testing import PRODUCTS_POI_INTEGRATION_TESTING
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectModifiedEvent

import unittest


class TestBase(unittest.TestCase):
    layer = PRODUCTS_POI_INTEGRATION_TESTING

    def rich_text(self, original):
        return RichTextValue(
            raw=original,
            mimeType="text/html",
            outputMimeType="text/html",
            encoding="utf-8",
        )

    def addMember(self, username, fullname, email, roles, last_login_time):
        # Taken from CMFPlone/tests/testMemberDataTool
        self.portal.portal_membership.addMember(username, "secret", roles, [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties(
            {
                "fullname": fullname,
                "email": email,
                "last_login_time": DateTime(last_login_time),
            }
        )

    def createTracker(
        self,
        folder,
        id,
        title=u"",
        description=u"",
        helpText=u"",
        availableAreas=None,
        availableIssueTypes=None,
        availableSeverities=None,
        defaultSeverity=u"Medium",
        availableReleases=None,
        assignees=None,
        sendNotificationEmails=False,
        mailingList=u"list@example.com",
    ):
        """Create a new tracker in the given folder"""
        if availableAreas is None:
            availableAreas = [
                {
                    "short_name": u"ui",
                    "title": u"User interface",
                    "description": u"User interface issues",
                },
                {
                    "short_name": u"functionality",
                    "title": u"Functionality",
                    "description": u"Issues with the basic functionality",
                },
                {
                    "short_name": u"process",
                    "title": u"Process",
                    "description": u"Issues relating to the development process itself",
                },
            ]
        if availableIssueTypes is None:
            availableIssueTypes = [
                {
                    "short_name": u"bug",
                    "title": u"Bug",
                    "description": u"Functionality bugs in the software",
                },
                {
                    "short_name": u"feature",
                    "title": u"Feature",
                    "description": u"Suggested features",
                },
                {
                    "short_name": u"patch",
                    "title": u"Patch",
                    "description": u"Patches to the software",
                },
            ]
        if availableSeverities is None:
            availableSeverities = [u"Critical", u"Important", u"Medium", u"Low"]
        if availableReleases is None:
            availableReleases = [u"2.0", u"1.0"]
        if assignees is None:
            assignees = []

        folder.invokeFactory("Tracker", id)
        tracker = getattr(folder, id)
        tracker.title = title
        tracker.description = description
        tracker.help_text = helpText
        tracker.available_areas = availableAreas
        tracker.available_issue_types = availableIssueTypes
        tracker.available_severities = availableSeverities
        tracker.default_severity = defaultSeverity
        tracker.available_releases = availableReleases
        tracker.assignees = assignees
        tracker.notification_emails = sendNotificationEmails
        tracker.mailing_list = mailingList
        tracker.reindexObject()
        notify(ObjectAddedEvent(tracker))

        return tracker

    def createIssue(
        self,
        tracker,
        title=u"An issue",
        details="Something is wrong",
        release=u"1.0",
        area=u"ui",
        issueType=u"bug",
        severity=u"Medium",
        targetRelease=u"2.0",
        steps=u"",
        attachment=None,
        contactEmail="submitter@example.com",
        watchers=None,
        tags=None,
        assignee=None,
    ):
        """Create an issue in the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        issue_id = next_issue_id(tracker)
        if watchers is None:
            watchers = []
        if tags is None:
            tags = []
        return api.content.create(
            id=issue_id,
            container=tracker,
            type="Issue",
            title=title,
            release=release,
            area=area,
            issue_type=issueType,
            severity=severity,
            target_release=targetRelease,
            details=self.rich_text(details),
            steps=self.rich_text(steps),
            attachment=attachment,
            watchers=watchers,
            contact_email=contactEmail,
            subject=tags,
            assignee=assignee,
        )
        # issue.reindexObject()
        # notify(ObjectAddedEvent(issue))
        # return issue

    def createResponse(
        self,
        issue,
        text="Response text",
        issueTransition="",
        newSeverity=None,
        newTargetRelease=None,
        newAssignee=None,
        attachment=None,
    ):
        """Create a response to the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        from Products.Poi.browser.response import Create

        request = issue.REQUEST
        # disable CSRF protection during tests
        alsoProvides(request, IDisableCSRFProtection)
        request.form["response"] = text
        request.form["transition"] = issueTransition
        if newSeverity is not None:
            request.form["severity"] = newSeverity
        if newTargetRelease is not None:
            request.form["targetRelease"] = newTargetRelease
        if newAssignee is not None:
            request.form["assignee"] = newAssignee
        if attachment is not None:
            request.form["attachment"] = attachment
        create_view = Create(issue, request)
        # A response is created by calling this view:
        create_view()

        container = IResponseContainer(issue)
        id = str(len(container) - 1)
        response = container[id]

        # In tests we need to fire this event manually:
        notify(ObjectModifiedEvent(response))
        return response
