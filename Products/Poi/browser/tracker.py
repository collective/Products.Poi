from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query
from DateTime import DateTime
from math import sqrt
import re


class IssueFolderView(BrowserView):

    def getFilteredIssues(self, criteria=None, sort_on_priority=True, **kwargs):
        """Get the contained issues in the given criteria.
        """
        context = aq_inner(self.context)
        query = self.buildIssueSearchQuery(criteria, **kwargs)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog.searchResults(query)

        if sort_on_priority:
            results = sorted(results, key=lambda i:(self.getPriorityForIssue(i), self.getSeverityMeasure(i)), reverse=True)
         
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
        query['path']        = '/'.join(context.getPhysicalPath())
        query['portal_type'] = ['PoiIssue']

        for k, v in allowedCriteria.items():
            if k in criteria:
                query[v] = criteria[k]
            elif v in criteria:
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
                op = subject['operator']
            except TypeError:
                # Fine: subject is a string or tuple.
                pass
            except KeyError:
                # No operator, so nothing can go wrong.
                pass
            else:
                try:
                    dummy = subject['query']
                except KeyError:
                    del query['Subject']

        query['sort_on'] = criteria.get('sort_on', 'created')
        query['sort_order'] = criteria.get('sort_order', 'reverse')
        if criteria.get('sort_limit'):
            query['sort_limit'] = criteria.get('sort_limit')

        return query

    def getMyIssues(self, openStates=['open', 'in-progress'],
                    memberId=None, manager=False):
        """Get a catalog query result set of my issues.

        So: all issues assigned to or submitted by the current user,
        with review state in openStates.

        If manager is True, add unconfirmed to the states.
        """
        context = aq_inner(self.context)
        if not memberId:
            mtool = getToolByName(context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            memberId = member.getId()

        if manager:
            if 'unconfirmed' not in openStates:
                openStates += ['unconfirmed']

        open = self.getFilteredIssues(state=openStates)
        issues = []

        for i in open:
            responsible = i.getResponsibleManager
            creator = i.Creator
            if memberId in (creator, responsible) or \
                   (manager and responsible == '(UNASSIGNED)'):
                issues.append(i)

        return issues

    def getOrphanedIssues(self, openStates=['open', 'in-progress'],
                          memberId=None):
        """Get a catalog query result set of orphaned issues.

        Meaning: all open issues not assigned to anyone and not owned
        by the given user.
        """
        context = aq_inner(self.context)
        if not memberId:
            mtool = getToolByName(context, 'portal_membership')
            member = mtool.getAuthenticatedMember()
            memberId = member.getId()

        open = self.getFilteredIssues(state=openStates)
        issues = []

        for i in open:
            responsible = i.getResponsibleManager
            creator = i.Creator
            if creator != memberId and responsible == '(UNASSIGNED)':
                issues.append(i)

        return issues

    def getPressureForIssue(self, issue):
        """ Calculates the pressure of an issue on its brain.
        
        Returns an integer as pressure state:
            1: Overdue
            2: Needs to be worked on today
            3: Still time left
        """
        if not issue.getDeadline:
            pressure = 3
        else:
            daysleft = self.getDaysLeft(issue)

            if daysleft < 0:
                pressure = 1
            elif daysleft < 2:
                pressure = 2
            else:
                pressure = 3

        return pressure

    te_re = re.compile( \
        r'\s*((?P<days>\d)+d)?\s*((?P<hours>\d)+h)?\s*((?P<minutes>\d)+m)?\s*')

    def getTimeEstimateDays(self, issue):
        """ Returns the time estimate of the given issue in hours.
        """
        
        if not issue.getTimeEstimate:
            return 0

        m = self.te_re.match(issue.getTimeEstimate)

        days = m.groupdict()['days'] or 0
        days = int(days)
        hours = m.groupdict()['hours'] or 0
        hours = int(hours)
        minutes = m.groupdict()['minutes'] or 0
        minutes = int(minutes)

        in_days = days + (hours / 24.) + (minutes / 1140.)
        return in_days


    def getDaysLeft(self, issue):
        """ Calculates how many days are left until the deadline for the
        given issue is reached.
        """

        today = DateTime()
        lstartdate = (issue.getDeadline - (self.getTimeEstimateDays(issue) * \
                        (1 - issue.getProgress / 100)))

        return( lstartdate - today ) 
        
    def getSchedulePressure(self, issue):
        """ Caculates a pressure measure for the given issue.
        The pressure depends on how many days are left until the 
        deadline for the issue is reached.
        """

        delta = self.getDaysLeft(issue)

        if delta < 0:  # overdue
            P = 7
        elif delta < 1:  # today
            P = 5
        elif delta < 3:  # within 3 days
            P = 3
        elif delta < 7:  # this week
            P = 2.5
        elif delta < 15:  # within 2 weeks
            P = 2
        elif delta < 30:  # this month
            P = 1.5
        elif delta < 90:  # this quarter
            P = 1
        elif delta < 180:  # this half year
            P = 1
        else:  # > 6 months
            P = 1
        return P

    def getSeverityMeasure(self, issue):
        """ Translates the severity value into an integer.
        """

        severity_vocab = self.context.getAvailableSeverities()
        severity_max = len(severity_vocab)
        lseverities = list(severity_vocab)
        return severity_max - lseverities.index(issue.getSeverity)
        
    def getPriorityForIssue(self, issue):
        """Calculates the priority of an issue on its brain. 
        
           The priority is dependent on the issues severity,
           schedule pressure and efford needed. 
        """

        S = self.getSeverityMeasure(issue)
        
        if issue.getDeadline:
            P = self.getSchedulePressure(issue)
        else:
            P = S

        E = self.getTimeEstimateDays(issue)

        if issue.getProgress:
            E = E * 0.01 * issue.getProgress

        priority = sqrt(2*S*S+2*P*P+E*E)/sqrt(5)
        return priority

