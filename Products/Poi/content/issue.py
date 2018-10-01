# -*- coding: utf-8 -*-
from zope.interface import implementer
from zope.interface import provider
from zope import schema

from Acquisition import aq_chain
from collective import dexteritytextindexer
from plone import api
from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.autoform.directives import write_permission, read_permission
from plone.autoform.directives import widget
from plone.dexterity.content import Container
from plone.schema import email

from plone.supermodel import model
from z3c.relationfield import RelationList, RelationChoice

from Products.Poi import PoiMessageFactory as _
from .tracker import ITracker
from .tracker import default_severity
from .tracker import possibleAreas
from .tracker import possibleIssueTypes
from .tracker import possibleSeverities
from .tracker import possibleTargetReleases
from .tracker import possibleAssignees


@provider(schema.interfaces.IContextSourceBinder)
def tracker_issues(context):
    """ vocabulary source for issues just inside this tracker
    """
    if ITracker.providedBy(context):
        current_tracker = context
    else:
        current_tracker = context.getTracker()
    path = '/'.join(current_tracker.getPhysicalPath())
    query = {'path': {'query': path},
             'object_provides': IIssue.__identifier__}
    return CatalogSource(**query)


@provider(schema.interfaces.IContextAwareDefaultFactory)
def default_watchers(context):
    creator = api.user.get_current()
    username = unicode(creator.getUserName())
    return [username]


def checkEmpty(value):
    """ Field should be empty
        or else we assume you are a bot
    """
    return True if value is False else False


class IIssue(model.Schema):
    """Marker interface for Poi issue"""

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'Poi_label_issue_title', default=u"Title"),
        description=_(u'Poi_help_issue_title',
                      default=u"Enter a short, descriptive title for "
                      u"the issue. A good title will make it easier "
                      u"for project managers to identify and respond "
                      u"to the issue.")
    )

    release = schema.Choice(
        title=_(u'Poi_label_issue_release', default=u'Release'),
        description=_(u'Poi_help_issue_release',
                      default=u"Select the version the issue was found in."),
        required=False,
        source=possibleTargetReleases
    )

    dexteritytextindexer.searchable('details')
    details = RichText(
        title=_(u'Poi_label_issue_details', default=u'Details'),
        description=_(u'Poi_help_issue_details',
                      default=u"Please provide further details.")
    )

    dexteritytextindexer.searchable('steps')
    steps = RichText(
        title=_(u'Poi_label_issue_steps', default=u'Steps To Reproduce'),
        description=_(u'Poi_help_issue_steps',
                      default=u"If applicable, please provide the steps to "
                      u"reproduce the error or identify the issue, one per "
                      u"line."),
        required=False,
    )

    area = schema.Choice(
        title=_(u'Poi_label_issue_area', default=u'Area'),
        description=_(u'Poi_help_issue_area',
                      default=u"Select the area this issue is relevant to."),
        source=possibleAreas
    )

    issue_type = schema.Choice(
        title=_(u'Poi_label_issue_type', default=u'Issue Type'),
        description=_(u'Poi_help_issue_type',
                      default=u"Select the type of issue."),
        source=possibleIssueTypes
    )

    read_permission(severity='Poi.ModifyIssueSeverity')
    write_permission(severity='Poi.ModifyIssueSeverity')
    severity = schema.Choice(
        title=_(u'Poi_label_issue_severity', default=u'Severity'),
        description=_(u'Poi_help_issue_severity',
                      default=u"Select the severity of this issue."),
        defaultFactory=default_severity,
        source=possibleSeverities
    )

    read_permission(target_release='Poi.ModifyIssueTargetRelease')
    write_permission(target_release='Poi.ModifyIssueTargetRelease')
    target_release = schema.Choice(
        title=_(u'Poi_label_issue_target_release', default=u'Target Release'),
        description=_(u'Poi_help_issue_target_release',
                      default=u"Release this issue is targetted to be fixed "
                              u"in."),
        source=possibleTargetReleases,
        required=False,
    )

    read_permission(assignee='Poi.ModifyIssueAssignment')
    write_permission(assignee='Poi.ModifyIssueAssignment')
    assignee = schema.Choice(
        title=_(u'Poi_label_issue_assignee', default=u'Assignee'),
        description=_(u'Poi_help_issue_assignee',
                      default=u"Select which person, if any, is assigned to "
                      u"this issue."),
        source=possibleAssignees,
        required=False,
    )

    contact_email = email.Email(
        title=_(u'Poi_label_issue_contact_email', default=u'Contact Email'),
        description=_(u'Poi_help_issue_contact_email',
                      default=u"Please provide an email address where you can "
                      u"be contacted for further information or when a "
                      u"resolution is available. Note that your email "
                      u"address will not be displayed to others."),
        required=False,
    )

    read_permission(watchers='Poi.ModifyIssueWatchers')
    write_permission(watchers='Poi.ModifyIssueWatchers')
    widget('watchers',
           AjaxSelectFieldWidget,
           vocabulary='plone.app.vocabularies.Users')
    watchers = schema.List(
        title=_(u'Poi_label_issue_watchers', default=u'Watchers'),
        description=_(u'Poi_help_issue_watchers',
                      default=u"Enter the user ids of members who are watching"
                      u" this issue, one per line. E-mail addresses are "
                      u"allowed too. These persons will "
                      u"receive an email when a response is added to the "
                      u"issue. Members can also add themselves as "
                      u"watchers."),
        value_type=schema.TextLine(),
        required=False,
        defaultFactory=default_watchers,
    )

    write_permission(subject='Poi.ModifyIssueTags')
    read_permission(subject='Poi.ModifyIssueTags')
    widget('subject',
           AjaxSelectFieldWidget,
           vocabulary='plone.app.vocabularies.Keywords',
           pattern_options={
               'allowNewItems': 'true'
           })
    subject = schema.Tuple(
        title=_(u'Poi_label_issue_subject', default=u'Subject'),
        description=_(u'Poi_help_issue_subject',
                      default=u"Tags can be used to add arbitrary "
                      u"categorisation to issues. The list below shows "
                      u"existing tags which you can select, or you can add "
                      u"new ones."),
        value_type=schema.TextLine(),
        required=False,
        missing_value=[],
    )

    read_permission(related_issue='Poi.ModifyRelatedIssues')
    write_permission(related_issue='Poi.ModifyRelatedIssues')
    widget('related_issue',
           RelatedItemsFieldWidget,
           pattern_options={
               'resultTemplate': '' +
                                 '<div class="   pattern-relateditems-result  <% if (selected) { %>pattern-relateditems-active<% } %>">' +
                                 '  <a href="#" class=" pattern-relateditems-result-select <% if (selectable) { %>selectable<% } %>">' +
                                 '    <% if (typeof getIcon !== "undefined" && getIcon) { %><img src="<%- getURL %>/@@images/image/icon "> <% } %>' +
                                 '    <span class="pattern-relateditems-result-title  <% if (typeof review_state !== "undefined") { %> state-<%- review_state %> <% } %>  " /span>' +
                                 '    <span class="pattern-relateditems contenttype-<%- portal_type.toLowerCase() %>"><%- Title %></span>' +
                                 '    <span class="pattern-relateditems-result-path"><%- path %></span>' +
                                 '  </a>' +
                                 ' </span>' +
                                 '</div>'})
    related_issue = RelationList(
        title=_(u'Poi_label_issue_related', default=u'Related Issue(s)'),
        description=_(u'Poi_help_issue_related',
                      default=u'Link related issues.'),
        value_type=RelationChoice(
            title=u"Related",
            source=tracker_issues,
        ),
        required=False
    )

    empty = schema.Bool(
        title=_(u'Poi_label_issue_empty', default=u'Leave this field empty'),
        required=False,
        constraint=checkEmpty
    )


@implementer(IIssue)
class Issue(Container):
    """
    An issue in the Poi Tracker
    """
    _tracker_uid = ''

    def getTracker(self):
        """Return the tracker."""
        tracker = api.content.get(UID=self._tracker_uid)
        if tracker:
            return tracker
        chain = aq_chain(self)
        for parent in chain:
            if ITracker.providedBy(parent):
                return parent

    def getContactEmail(self):
        return api.user.get(self.Creator()).getProperty('email')

    def getReviewState(self):
        """get the current workflow state of the issue"""
        wftool = api.portal.get_tool('portal_workflow')
        state = wftool.getInfoFor(self, 'review_state')
        title = wftool.getTitleForStateOnType(state, self.portal_type)
        return {
            'state': state,
            'title': title,
        }

    def display_area(self):
        tracker = self.getTracker()
        area = possibleAreas(tracker).by_value.get(self.area)
        if area:
            return area.title
        return '(missing)'

    def display_issue_type(self):
        tracker = self.getTracker()
        issue_type = possibleIssueTypes(tracker).by_value.get(self.issue_type)
        if issue_type:
            return issue_type.title
        return '(missing)'

    def isWatching(self):
        """
        Determine if the current user is watching this issue or not.
        """
        portal_membership = api.portal.get_tool('portal_membership')
        member = portal_membership.getAuthenticatedMember()
        return member.getId() in self.watchers

    def isValid(self):

        """Check if the response is valid.

        Meaning: a response has been filled in.
        """
        errors = schema.getValidationErrors(IIssue, self)
        if errors:
            return False
        else:
            return True

    def linkedDetails(self):
        tracker = self.getTracker()
        try:
            return tracker.linkDetection(self.details.output)
        except AttributeError:
            return tracker.linkDetection(self.details)

    def linkedSteps(self):
        tracker = self.getTracker()
        try:
            return tracker.linkDetection(self.steps.output)
        except:
            return tracker.linkDetection(self.steps)

# this is implemented here to reduce the chance of a circular
# import with IIssue
def next_issue_id(tracker):
    """find the next available issue ID (integer) for a Poi tracker"""
    issue_id = 1
    issues = api.content.find(context=tracker, object_provides=IIssue)
    existing_ids = [int(issue.id) for issue in issues if issue.id.isdigit()]
    if len(existing_ids):
        issue_id = max(existing_ids) + 1
    return str(issue_id)
