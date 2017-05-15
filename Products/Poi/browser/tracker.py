from urllib import urlencode
from urlparse import parse_qsl

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.PythonScripts.standard import url_quote
from ZTUtils import make_query

from plone import api

from Products.Poi.content.issue import IIssue


ACTIVE_STATES = ['open', 'in-progress', 'unconfirmed']


class IssueFolderView(BrowserView):

    def getActiveStates(self):
        return ACTIVE_STATES

    def getFilteredIssues(self, criteria=None, **kwargs):
        """Get the contained issues in the given criteria.
        """
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        return api.content.find(**query)

    def getSortedFilteredIssues(self, criteria=None, **kwargs):
        """Get the contained issues in the given criteria with a custom sort.
        """

        if criteria:
            newresults = []
            sort_order = criteria.get('sort_order') == 'reverse'

            # if sorting by assignee, use the human-friendly name
            if criteria.get('sort_on') == 'assignee':
                results = self.getFilteredIssues(criteria, **kwargs)
                context = aq_inner(self.context)
                membership = getToolByName(context, 'portal_membership')
                for i in results:
                    member_info = membership.getMemberInfo(i.assignee)
                    if member_info:
                        fullname = member_info.get('fullname', '')
                    else:
                        fullname = i.assignee
                    newresults.append((i, fullname))

                results = [dict(brain=r[0],
                                slug=r[1]) for r in
                           sorted((i for i in newresults),
                                  key=lambda x: x[1], reverse=sort_order)]
            # if sorting by Subject/tags, do it as a string
            elif criteria.get('sort_on') == 'subject_tags':
                criteria.set('sort_on', 'id')
                results = self.getFilteredIssues(criteria, **kwargs)
                for i in results:
                    sorted_tags = sorted((y for y in i.Subject),
                                         key=lambda x: x)
                    string_tags = ", ".join(sorted_tags)
                    newresults.append((i, string_tags))

                results = [dict(brain=r[0],
                                slug=r[1]) for r in
                           sorted((i for i in newresults),
                                  key=lambda x: x[1], reverse=sort_order)]
            elif criteria.get('sort_on') == 'id':
                results = self.getFilteredIssues(criteria, **kwargs)
                for i in results:
                    id_as_number = int(i.id)
                    newresults.append((i, id_as_number))

                results = [dict(brain=r[0],
                                slug=r[1]) for r in
                           sorted((i for i in newresults),
                                  key=lambda x: x[1], reverse=sort_order)]
            else:
                results = self.getFilteredIssues(criteria, **kwargs)
        else:
            results = self.getFilteredIssues(criteria, **kwargs)

        return results

    def getIssueSearchQueryString(self, criteria=None, **kwargs):
        """Return a query string for an issue query.

        Form of return string:name1=value1&name2=value2
        """
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        return make_query(query)

    def buildIssueSearchQuery(self, criteria=None, **kwargs):
        """Build canonical query for issue search.
        """
        context = aq_inner(self.context)

        if criteria is None:
            criteria = kwargs
        else:
            criteria = dict(criteria)

        allowedCriteria = {
            'release': 'release',
            'area': 'area',
            'issueType': 'issue_type',
            'severity': 'severity',
            'targetRelease': 'target_release',
            'state': 'review_state',
            'tags': 'Subject',
            'responsible': 'assignee',
            'creator': 'Creator',
            'text': 'SearchableText',
            'id': 'getId',
        }

        query = {}
        query['path'] = query['path'] = '/'.join(context.getPhysicalPath())
        query['object_provides'] = IIssue

        for k, v in allowedCriteria.items():
            if criteria.get(k):
                if criteria[k] == '(UNASSIGNED)':
                    continue
                query[v] = criteria[k]
            elif criteria.get(v):
                query[v] = criteria[v]

        # Playing nicely with the form.

        # Subject can be a string of one tag, a tuple of several tags
        # or a dict with a required query and an optional operator
        # 'and/or'.  We must avoid the case of the dict with only the
        # operator and no actual query, else we will suffer from
        # KeyErrors.  Actually, when coming from the
        # poi_issue_search_form, instead of say from a test, its type
        # is not 'dict', but 'instance', even though it looks like a
        # dict.  See http://plone.org/products/poi/issues/137
        if 'Subject' in query:
            subject = query['Subject']
            # We cannot use "subject.has_key('operator')" or
            # "'operator' in subject'" because of the strange
            # instance.
            try:
                subject['operator']
            except TypeError:
                # Fine: subject is a string or tuple.
                pass
            except KeyError:
                # No operator, so nothing can go wrong.
                pass
            else:
                try:
                    subject['query']
                except KeyError:
                    del query['Subject']

        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')
        if criteria.get('sort_limit'):
            query['sort_limit'] = criteria.get('sort_limit')
        # allow substring searches
        if 'exacttext' not in criteria and 'SearchableText' in query:
            query['SearchableText'] = '*{}*'.format(query['SearchableText'])

        return query

    def getMyIssues(self, openStates=['unconfirmed', 'open', 'in-progress'],
                    memberId=None, manager=False):
        """Get a catalog query result set of my issues.

        So: all issues assigned to the current user,
        with review state in openStates.
        """
        if not memberId:
            memberId = api.user.get_current().id

        issues = []

        for i in self.getFilteredIssues(state=openStates):
            assignee = i.assignee
            if not assignee:
                continue
            if memberId in assignee or (manager and assignee == '(UNASSIGNED)'):
                issues.append(i)

        return issues

    def getMySubmitted(self, openStates=['unconfirmed', 'open', 'in-progress'],
                       memberId=None, manager=False):
        """Get a catalog query result set of my issues.

        So: all issues submitted by the current user,
        with review state in openStates.
        """
        if not memberId:
            memberId = api.user.get_current().id

        issues = []

        for i in self.getFilteredIssues(state=openStates):
            assignee = i.assignee
            creator = i.Creator
            if memberId in creator or (manager and assignee == '(UNASSIGNED)'):
                issues.append(i)

        return issues

    def getOrphanedIssues(self, openStates=['unconfirmed', 'open', 'in-progress'],
                          memberId=None):
        """Get a catalog query result set of orphaned issues.

        Meaning: all open issues not assigned to anyone. Displayed
        to Managers and Assignees
        """
        if not memberId:
            memberId = api.user.get_current().id

        issues = []

        isManager = api.user.get_current().has_role('Manager')
        isAssignee = memberId in self.aq_parent.assignees
        if isManager or isAssignee:
            for i in self.getFilteredIssues(state=openStates):
                assignee = i.assignee
                if not assignee:
                    issues.append(i)

        return issues

    def getBaseQuery(self):
        query = self.request.QUERY_STRING
        if query:
            params = parse_qsl(query)
            params = [i for i in params if i[0] != 'sort_on']
            params = [i for i in params if i[0] != 'sort_order']
            params = [i for i in params if i[0] != '_authenticator']
            return urlencode(params)
        else:
            return ""


class QuickSearchView(BrowserView):
    """Parse a quicksearch string and jump to the appropriate issue or
    search result page.

    """

    def __call__(self):
        tracker = aq_inner(self.context)
        search_text = self.request.form.get('searchText', '')
        issue_id = search_text
        if issue_id.startswith('#'):
            issue_id = issue_id[1:]
        base_url = tracker.absolute_url()
        if issue_id in tracker.keys():
            url = '%s/%s' % (base_url, issue_id)
        else:
            url = '%s/poi_issue_search?SearchableText=%s' % (
                base_url, url_quote(search_text))
        self.request.RESPONSE.redirect(url)
