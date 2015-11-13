# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope import schema

from plone.app.textfield import RichText
from plone.autoform.directives import widget
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.z3cform.textlines import TextLinesFieldWidget

from Acquisition import aq_chain
from Products.Poi import PoiMessageFactory as _
from .tracker import ITracker
from .tracker import possibleAreas
from .tracker import possibleIssueTypes
from .tracker import possibleSeverities
from .tracker import possibleTargetReleases
from .tracker import possibleAssignees


class IIssue(model.Schema):
    """Marker interface for Poi issue"""

    title = schema.TextLine(
        title=(u'Title'),
        description=_(u"Enter a short, descriptive title for the issue. "
                     u"A good title will make it easier for project "
                     u"managers to identify and respond to the issue.")
    )

    release = schema.TextLine(
        title=_(u'Release'),
        description=_(u"Select the version the issue was found in."),
        required=False,
    )

    details = RichText(
        title=_(u'Details'),
        description=_(u"Please provide further details")
    )

    steps = RichText(
        title=_(u'Steps To Reproduce'),
        description=_(u"If applicable, please provide the steps to "
                      u"reproduce the error or identify the issue, one per "
                      u"line.")
    )

    area = schema.Choice(
        title=_(u'Area'),
        description=_(u"Select the area this issue is relevant to."),
        source=possibleAreas
    )

    issue_type = schema.Choice(
        title=_(u'Issue Type'),
        description=_(u"Select the type of issue."),
        source=possibleIssueTypes
    )

    severity = schema.Choice(
        title=_(u'Severity'),
        description=_(u"Select the severity of this issue."),
        source=possibleSeverities
    )

    target_release = schema.Choice(
        title=_(u'Target Release'),
        description=_(u"Release this issue is targetted to be fixed in"),
        source=possibleTargetReleases,
        required=False,
    )

    assignee = schema.Choice(
        title=_(u'Assignee'),
        description=_(u"Select which person, if any, is assigned to"
                      u"this issue."),
        source=possibleAssignees
    )

    widget(watchers=TextLinesFieldWidget)
    watchers = schema.List(
        title=_(u'Watchers'),
        description=_(u"Enter the user ids of members who are watching "
                      u"this issue, one per line. E-mail addresses are "
                      u"allowed too. These persons will "
                      u"receive an email when a response is added to the "
                      u"issue. Members can also add themselves as "
                      u"watchers."),
        value_type=schema.TextLine(),
        required=False,
    )

    widget(subject=TextLinesFieldWidget)
    subject = schema.List(
        title=_(u'Subject'),
        description=_(u"Tags can be used to add arbitrary categorisation to "
                      u"issues. The list below shows existing tags which "
                      u"you can select, or you can add new ones."),
        value_type=schema.TextLine(),
        required=False,
    )


@implementer(IIssue)
class Issue(Container):
    """
    An issue in the Poi Tracker
    """

    def getTracker(self):
        """Return the tracker.

        This gets around the problem that the aq_parent of an issue
        that is being created is not the tracker, but a temporary
        folder.
        """
        for parent in aq_chain(self):
            if ITracker.providedBy(parent):
                return parent
        raise Exception(
            "Could not find PoiTracker in acquisition chain of %r" %
            self)
