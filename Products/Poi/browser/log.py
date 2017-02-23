from datetime import datetime

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from Products.Poi.adapters import IResponseContainer


def fixDate(date):
    if isinstance(date, basestring):
        # Should not happen, but I have seen it locally, and I am
        # not sure if that was just the result of temporarily
        # wrong code or something more important.
        date = DateTime(date)
    return date


def convertDate(date):
    return datetime(date.year(), date.month(), date.day(), date.hour(),
                    date.minute())


def getEntrySortingKey(entry):
    if not hasattr(entry, 'portal_type'):
        # response
        key = entry.get('date')
    else:
        # issue
        key = entry.created

    if callable(key):
        key = key()

    return key


class LogView(BrowserView):

    @property
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    def getTimeDelta(self, zope_date):
        date = convertDate(zope_date)
        now = datetime.now()

        delta = now - date

        # use largest time unit
        minutes = 0
        hours = 0
        days = delta.days

        if not days:
            hours = delta.seconds / 3600
        if not hours and not days:
            minutes = delta.seconds / 60

        return {'minutes': minutes,
                'hours': hours,
                'days': days}

    def getPrettyName(self, username=None, user=None):
        if not username and not user:
            raise ValueError('Both username and user cannot be empty')

        if username:
            portal_membership = getToolByName(self.context,
                                              'portal_membership')
            user = portal_membership.getMemberById(username)

        if user is None:
            # Anonymous
            return username
        return user.getProperty('fullname') or user.getUserName()

    def getLogEntries(self, count=20):
        context = aq_inner(self.context)
        issuefolder = context.restrictedTraverse('@@issuefolder')
        # First we get the most recently modified issues, which means
        # the most recently added, or the ones with the most recent
        # responses.
        issues = [i.getObject() for i in issuefolder.getFilteredIssues(
            sort_on='modified', sort_limit=count, sort_order='reverse')]

        responses = []
        for issue in issues:
            folder = IResponseContainer(issue)
            for res in list(folder):
                if not res:
                    continue
                item = dict(
                    parent=issue,
                    response=res,
                    date=fixDate(res.date))
                responses.append(item)

        items = responses + issues

        # sort entries
        items.sort(key=getEntrySortingKey, reverse=True)

        results = []
        for item in items[:count]:
            if not hasattr(item, 'portal_type'):
                # Response
                date = item.get('date')
                issue = item.get('parent')
                response = item.get('response')
                data = {'type': 'response',
                        'author': self.getPrettyName(response.creator),
                        'date': date,
                        'timedelta': self.getTimeDelta(date),
                        'changes': response.changes,
                        'issue': issue.title_or_id(),
                        'url': issue.absolute_url(),
                        'text': response.rendered_text}
            else:
                # Issue
                data = {'title': item.title_or_id(),
                        'type': item.portal_type,
                        'author': self.getPrettyName(item.Creator()),
                        'date': item.created(),
                        'url': item.absolute_url(),
                        'timedelta': self.getTimeDelta(item.created()),
                        'text': item.details}

            results.append(data)

        return results
