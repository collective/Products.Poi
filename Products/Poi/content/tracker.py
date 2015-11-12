# -*- coding: utf-8 -*-
#
# File: tracker.py
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

__author__ = """Rob McBroom <rob@sixfeetup.com>"""
__docformat__ = 'plaintext'


from zope.interface import implementer
from zope import schema
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from Products.Poi import PoiMessageFactory as _
from Products.Poi import permissions
from plone.app.textfield import RichText
from plone.autoform.directives import widget
from plone.autoform.directives import write_permission
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.z3cform.textlines import TextLinesFieldWidget
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow


def possibleAreas(context):
    """
    Get the available areas as a Vocabulary.
    """
    tracker = context.getTracker()
    terms = [(tt.id, tt.title) for tt in tracker.available_areas]
    return SimpleVocabulary.fromItems(terms)


def possibleIssueTypes(context):
    """
    Get the available issue types as a Vocabulary.
    """
    tracker = context.getTracker()
    terms = [(tt.id, tt.title) for tt in tracker.available_issue_types]
    return SimpleVocabulary.fromItems(terms)


def possibleSeverities(context):
    """
    Get the available severities as a Vocabulary.
    """
    tracker = context.getTracker()
    return SimpleVocabulary.fromValues(tracker.available_severities)


def possibleTargetReleases(context):
    """
    Get the available target release as a Vocabulary.
    """
    tracker = context.getTracker()
    return SimpleVocabulary.fromValues(tracker.available_releases)


def possibleAssignees(context):
    """
    Get the available assignees as a DispayList.
    """
    tracker = context.getTracker()
    return SimpleVocabulary.fromValues(tracker.assignees)

directlyProvides(possibleAreas, IContextSourceBinder)
directlyProvides(possibleIssueTypes, IContextSourceBinder)
directlyProvides(possibleSeverities, IContextSourceBinder)
directlyProvides(possibleTargetReleases, IContextSourceBinder)
directlyProvides(possibleAssignees, IContextSourceBinder)


class IBasicData(Interface):
    short_name = schema.TextLine(
        title=_(u'Short Name'),
    )
    title = schema.TextLine(
        title=_(u'Title'),
    )
    description = schema.TextLine(
        title=_(u'Description'),
        required=False,
    )


class ITracker(model.Schema):
    title = schema.TextLine(
        title=_(u'title'),
        description=_(
            u'Poi_help_tracker_title',
            default=u"Enter a descriptive name for this tracker"
        ),
    )

    description = RichText(
        title=_(u'description'),
        description=_(
            u'Poi_help_tracker_description',
            default=u"Describe the purpose of this tracker"
        ),
    )

    help_text = RichText(
        title=_(u'help_text'),
        description=_(
            u'Poi_help_helpText',
            default=(u"Enter any introductory help text you'd like to "
                     u"display on the tracker front page.")
        ),
    )

    widget(available_areas=DataGridFieldFactory)
    available_areas = schema.List(
        title=_(u'Poi_label_availableAreas',
                default=u"Areas"),
        description=_(
            u'Poi_help_availableAreas',
            default="Enter the issue topics/areas for this tracker."
        ),
        value_type=DictRow(title=_(u'Area'), schema=IBasicData),
    )

    widget(available_issue_types=DataGridFieldFactory)
    available_issue_types = schema.List(
        title=_(u'Poi_label_availableIssueTypes',
                default=u"Issue types"),
        description=_(
            u'Poi_help_availableIssueTypes',
            default=u"Enter the issue types for this tracker."
        ),
        value_type=DictRow(title=_(u'Issue Type'), schema=IBasicData),
    )

    widget(available_severities=TextLinesFieldWidget)
    available_severities = schema.List(
        title=_(u'Poi_label_availableSeverities',
                default=u"Available severities"),
        default=[_(u'Critical'), _(u'Important'), _(u'Medium'), _(u'Low')],
        description=_(
            u'Poi_help_availableSeverities',
            default=(u"Enter the different type of issue severities "
                     u"that should be available, one per line.")
        ),
    )

    default_severity = schema.Choice(
        title=_(
            u'Poi_label_defaultSeverity',
            default=u"Default severity",
        ),
        default=_(u'Medium'),
        description=_(
            u'Poi_help_defaultSeverity',
            default=u"Select the default severity for new issues."
        ),
        source=possibleSeverities,
    )

    widget(available_releases=TextLinesFieldWidget)
    available_releases = schema.List(
        title=_(
            u'Poi_label_availableReleases',
            default=u'Available Releases'
        ),
        description=_(
            u'Poi_help_availableReleases',
            default=(
                u"Enter the releases which issues can be assigned to, "
                u"one per line. If no releases are entered, issues "
                u"will not be organized by release.")
        ),
        required=False,
    )

    widget(assignees=TextLinesFieldWidget)
    assignees = schema.List(
        title=_(u'Poi_label_assignees', default=u'Assignees'),
        description=_(u'Users assigned to this issue'),
    )

    write_permission(watchers=permissions.ModifyIssueWatchers)
    widget(watchers=TextLinesFieldWidget)
    watchers = schema.List(
        title=_(u'Poi_label_tracker_watchers'),
        description=_(
            u'Poi_help_tracker_watchers',
            default=(
                u"Enter the user ids of members who are watching "
                u"this tracker, one per line. E-mail addresses are "
                u"allowed too. These persons will receive "
                u"an email when an issue or response is added to the "
                u"tracker. Members can also add themselves as "
                u"watchers.")
        ),
    )

    notification_emails = schema.Bool(
        title=_(
            u'Poi_label_sendNotificationEmails',
            default=u"Send notification emails"
        ),
        description=_(
            u'Poi_help_sendNotificationEmails',
            default=(
                u"If selected, tracker managers will receive an email "
                u"each time a new issue or response is posted, and "
                u"issue submitters will receive an email when there "
                u"is a new response and when an issue has been "
                u"resolved, awaiting confirmation. Technicians will "
                u"get an email when an issue is assigned to them.")
        ),
    )

    # TODO validation?
    mailing_list = schema.TextLine(
        title=_(
            u'Poi_label_mailingList',
            default=u"Mailing list"
        ),
        description=_(
            u'Poi_help_mailingList',
            default=(
                u"If given, and if 'Send notification emails' is "
                u"selected, an email will be sent to this address "
                u"each time a new issue or response is posted. "
                u"Managers will receive individual emails as well. "
                u"If this is not wanted, you may want to make them "
                u"technician instead.")
        ),
        required=False,
    )

    repo_url = schema.TextLine(
        title=_(u'Poi_label_svnurl',
                default=u"URL to Repository"),
        description=_(
            u'Poi_help_svnurl',
            default=(
                u"Please enter the URL to the related repository, "
                u"e.g.: "
                u"http://dev.plone.org/changeset/%(rev)s/collective "
                u"for products in the Plone collective.")
        ),
    )


@implementer(ITracker)
class Tracker(Container):
    """
    An issue in the Poi Tracker
    """
