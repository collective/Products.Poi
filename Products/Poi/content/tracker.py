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


from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import implementer
from zope import schema
from zope.interface import implements
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import directlyProvides
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from borg.localrole.interfaces import ILocalRoleProvider

from collections import Counter
from Products.Poi import PoiMessageFactory as _
from plone import api
from Products.Poi.utils import is_email
from Products.Poi.utils import link_bugs
from Products.Poi.utils import link_repo
from plone.app.textfield import RichText
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.autoform.directives import widget
from plone.autoform.directives import write_permission, read_permission
from plone.dexterity.content import Container
from plone.protect.utils import addTokenToUrl
from plone.supermodel import model
from plone.z3cform.textlines import TextLinesFieldWidget
from collective.z3cform.datagridfield import DataGridFieldFactory, DictRow
from z3c.form import validator


DEFAULT_SEVERITIES = [
    _(u'Critical'),
    _(u'Important'),
    _(u'Medium'),
    _(u'Low')
]


def possibleAreas(context):
    """
    Get the available areas as a Vocabulary.
    """
    if ITracker.providedBy(context):
        tracker = context
    elif hasattr(context, 'getTracker'):
        tracker = context.getTracker()
    else:
        return SimpleVocabulary.fromValues([])
    terms = [
        SimpleTerm(value=tt.get('short_name'), title=tt.get('title'))
        for tt in tracker.available_areas
        if tt.get('short_name') is not None
    ]
    return SimpleVocabulary(terms)


def possibleIssueTypes(context):
    """
    Get the available issue types as a Vocabulary.
    """
    if ITracker.providedBy(context):
        tracker = context
    elif hasattr(context, 'getTracker'):
        tracker = context.getTracker()
    else:
        return SimpleVocabulary.fromValues([])
    terms = [
        SimpleTerm(value=tt.get('short_name'), title=tt.get('title'))
        for tt in tracker.available_issue_types
        if tt.get('short_name') is not None
    ]
    return SimpleVocabulary(terms)


@provider(IContextAwareDefaultFactory)
def default_severity(context):
    """
    Get the default severity.
    """
    if hasattr(context, 'default_severity'):
        tracker = context
        return tracker.default_severity
    return DEFAULT_SEVERITIES[0]


def possibleSeverities(context):
    """
    Get the available severities as a Vocabulary.
    """
    if ITracker.providedBy(context):
        tracker = context
    elif hasattr(context, 'getTracker'):
        tracker = context.getTracker()
    elif hasattr(context, 'context'):
        tracker = context.context.getTracker()
    else:
        return SimpleVocabulary.fromValues(DEFAULT_SEVERITIES)
    return SimpleVocabulary.fromValues(tracker.available_severities)


def possibleTargetReleases(context):
    """
    Get the available target release as a Vocabulary.
    """
    if ITracker.providedBy(context):
        tracker = context
    elif hasattr(context, 'getTracker'):
        tracker = context.getTracker()
    else:
        return SimpleVocabulary.fromValues([])
    if tracker.available_releases:
        return SimpleVocabulary.fromValues(tracker.available_releases)
    return SimpleVocabulary([])


def possibleAssignees(context):
    """
    Get the available assignees as a DispayList.
    """
    if ITracker.providedBy(context):
        tracker = context
    elif hasattr(context, 'getTracker'):
        tracker = context.getTracker()
    else:
        return SimpleVocabulary.fromValues([])
    assignees = []
    for pa in tracker.assignees:
        user = api.user.get(pa)
        if user:
            fullname = user.getProperty('fullname')
        else:
            fullname = pa
        term = SimpleTerm(value=pa, title=fullname)
        assignees.append(term)
    return SimpleVocabulary(assignees)

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
        title=_(u'title', default=u'Title'),
        description=_(
            u'Poi_help_tracker_title',
            default=u"Enter a descriptive name for this tracker"
        ),
    )

    description = schema.Text(
        title=_(u'description', default=u'Description'),
        description=_(
            u'Poi_help_tracker_description',
            default=u"Describe the purpose of this tracker"
        ),
        required=False,
    )

    help_text = RichText(
        title=_(u'help_text', default=u'Help Text'),
        description=_(
            u'Poi_help_helpText',
            default=(u"Enter any introductory help text you'd like to "
                     u"display on the tracker front page.")
        ),
        required=False,
    )

    widget(available_areas=DataGridFieldFactory)
    available_areas = schema.List(
        title=_(u'Poi_label_availableAreas',
                default=u"Areas"),
        description=_(
            u'Poi_help_availableAreas',
            default="Enter the issue topics/areas for this tracker."
        ),
        default=[
            {'short_name': 'ui',
             'title': 'User interface',
             'description': 'User interface issues'},
            {'short_name': 'functionality',
             'title': 'Functionality',
             'description': 'Issues with the basic functionality'},
            {'short_name': 'process',
             'title': 'Process',
             'description':
             'Issues relating to the development process itself'},
        ],
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
        default=[
            {'short_name': 'bug',
             'title': 'Bug',
             'description': 'Functionality bugs in the software'},
            {'short_name': 'feature',
             'title': 'Feature',
             'description': 'Suggested features'},
            {'short_name': 'patch',
             'title': 'Patch',
             'description': 'Patches to the software'},
        ],
        value_type=DictRow(title=_(u'Issue Type'), schema=IBasicData),
    )

    widget(available_severities=TextLinesFieldWidget)
    available_severities = schema.List(
        title=_(u'Poi_label_availableSeverities',
                default=u"Available severities"),
        default=DEFAULT_SEVERITIES,
        description=_(
            u'Poi_help_availableSeverities',
            default=(u"Enter the different type of issue severities "
                     u"that should be available, one per line.")
        ),
        value_type=schema.TextLine(),
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
            default=u'Available releases'
        ),
        description=_(
            u'Poi_help_availableReleases',
            default=(
                u"Enter the releases which issues can be assigned to, "
                u"one per line. If no releases are entered, issues "
                u"will not be organized by release.")
        ),
        value_type=schema.TextLine(),
        required=False,
    )

    widget(
        'assignees',
        AjaxSelectFieldWidget
    )
    assignees = schema.List(
        title=_(u'Poi_label_assignees', default=u'Assignees'),
        description=_(u"Enter users who will be responsible for solving "
                      u"the issues. Users also need to be added as "
                      u"Watchers to receive notifications."),
        value_type=schema.Choice(
            source='plone.app.vocabularies.Users'
            ),
    )

    read_permission(watchers='Poi.ModifyIssueWatchers')
    write_permission(watchers='Poi.ModifyIssueWatchers')
    widget('watchers',
           AjaxSelectFieldWidget,
           vocabulary='plone.app.vocabularies.Users')
    watchers = schema.List(
        title=_(u'Poi_label_tracker_watchers', default=u'Watchers'),
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
        value_type=schema.TextLine(),
        required=False,
    )

    notification_emails = schema.Bool(
        title=_(
            u'Poi_label_sendNotificationEmails',
            default=u"Send notification emails"
        ),
        description=_(
            u'Poi_help_sendNotificationEmails',
            default=(
                u"If selected, all tracker assignees above will "
                u"receive an email for new issues and all issue "
                u"responses. Issue watchers will receive an email "
                u"for all issue responses. Issue submitters will "
                u"receive an email when the issue has been resolved.")
        ),
    )

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
                u"each time a new issue or response is posted.")
        ),
        required=False,
        constraint=is_email,
    )

    repo_url = schema.TextLine(
        title=_(u'Poi_label_svnurl',
                default=u"URL to Repository"),
        description=_(
            u'Poi_help_svnurl',
            default=(
                u"Please enter the URL to the related repository, "
                u"e.g.: "
                u"https://github.com/collective/Products.Poi/commit/%(rev)s "
                u"for Products.Poi.")
        ),
        required=False,
    )


@implementer(ITracker)
class Tracker(Container):
    """
    A Poi Tracker
    """

    def getIssues(self):
        """get issues belonging to this tracker"""
        return api.content.find(
            portal_type='Issue',
            context=self,
        )

    def getAllTags(self):
        """return all site tags"""
        pc = api.portal.get_tool('portal_catalog')
        key_indexes = pc._catalog.indexes['Subject']
        return [i[0] for i in key_indexes.items()]

    def getTagsInUse(self):
        """Get a list of the issue tags in use in this tracker."""
        tags = Counter()
        for i in self.getIssues():
            tags += Counter(i.Subject)
        return tags.most_common(10)

    def getIssueWorkflowStates(self):
        """Get a DisplayList of the workflow states available on issues."""
        portal_workflow = api.portal.get_tool(name='portal_workflow')
        chain = portal_workflow.getChainForPortalType('Issue')
        workflow = getattr(portal_workflow, chain[0])
        states = getattr(workflow, 'states')
        vocab = []
        for id, state in states.items():
            vocab.append((id, state.title))
        return vocab

    def isUsingReleases(self):
        """Return a boolean indicating whether this tracker is using releases.
        """
        return bool(self.available_releases)

    def getReleasesVocab(self):
        """
        Get the releases available to the tracker as a DisplayList.
        """
        items = possibleTargetReleases(self)
        return SimpleVocabulary(items)

    def getAssigneesVocab(self):
        items = possibleAssignees(self)
        return SimpleVocabulary(items)

    def addTokenToUrl(self, original_url):
        return addTokenToUrl(original_url)

    def linkDetection(self, text):
        issues = self.getIssues()
        ids = {issue.id for issue in issues}
        text = link_bugs(text, ids, base_url=self.absolute_url())
        if self.repo_url:
            text = link_repo(text, self.repo_url)
        return text


class TrackerRoleProvider(object):
    """ role provider to give all Assignees the Technician role
    """
    implements(ILocalRoleProvider)
    adapts(ITracker)

    def __init__(self, context):
        self.context = context
        self.roles = (u'Technician',)

    def getRoles(self, user_id):
        try:
            if user_id not in self.context.assignees:
                return ()
        except AttributeError:
            return ()
        return self.roles

    def getAllRoles(self):
        if not self.context.assignees:
            yield '', ()
            return
        for assignee in self.context.assignees:
            try:
                yield assignee, self.roles
            except AttributeError:
                yield '', ()


class AlphaNumericValidator(validator.SimpleFieldValidator):
    """Only allow letters, numbers, hyphens, and underscores
    """

    def validate(self, value):
        allowed_chars = "abcdefghijklmnopqrstuvwxyz"
        allowed_chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789_-"
        if not value:
            return
        error = False
        for val in value:
            if val['short_name']:
                error = any(c not in allowed_chars for c in val['short_name'])
            if val['title']:
                error = any(c not in allowed_chars for c in val['title'])
        if error:
            errtext = u"Please enter only alpha-numeric characters into this \
                       field, no special characters other than hyphens and \
                       underscores"
            raise Invalid(errtext)
        else:
            return


class AlphaNumericValidator2(validator.SimpleFieldValidator):
    """Only allow letters, numbers, hyphens, and underscores
    """

    def validate(self, value):
        allowed_chars = "abcdefghijklmnopqrstuvwxyz"
        allowed_chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789_-"
        if not value:
            return
        error = False
        for val in value:
            if val['short_name']:
                error = any(c not in allowed_chars for c in val['short_name'])
            if val['title']:
                error = any(c not in allowed_chars for c in val['title'])
        if error:
            errtext = u"Please enter only alpha-numeric characters into this \
                       field, no special characters other than hyphens and \
                       underscores"
            raise Invalid(errtext)
        else:
            return


class AlphaNumericLinesValidator(validator.SimpleFieldValidator):
    """Only allow letters, numbers, hyphens, and underscores
    """

    def validate(self, value):
        allowed_chars = "abcdefghijklmnopqrstuvwxyz"
        allowed_chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789_-"
        if not value:
            return
        error = False
        for val in value:
            if any(c not in allowed_chars for c in val):
                error = True
        if error:
            errtext = u"Please enter only alpha-numeric characters into this \
                       field, no special characters other than hyphens and \
                       underscores"
            raise Invalid(errtext)
        else:
            return

# can't use a validator multiple times, or I don't know how
# see https://github.com/zopefoundation/z3c.form/issues/61
validator.WidgetValidatorDiscriminators(
    AlphaNumericValidator, field=ITracker['available_areas'])
validator.WidgetValidatorDiscriminators(
    AlphaNumericValidator2, field=ITracker['available_issue_types'])
validator.WidgetValidatorDiscriminators(
    AlphaNumericLinesValidator, field=ITracker['available_severities'])
provideAdapter(AlphaNumericValidator)
provideAdapter(AlphaNumericValidator2)
provideAdapter(AlphaNumericLinesValidator)
