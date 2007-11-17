from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from datetime import datetime

def convertDate(date):
    return datetime(date.year(), date.month(), date.day(), date.hour(), date.minute())

def getEntrySortingKey(entry):
    if entry.portal_type == 'PoiResponse':
        key = entry.modified
    else:
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
        
        delta = now-date

        # use largest time unit
        minutes = 0
        hours = 0
        days = delta.days

        if not days: hours = delta.seconds/3600
        if not hours and not days: minutes = delta.seconds/60

        return {'minutes': minutes,
                'hours': hours,
                'days': days}
        
    def getPrettyName(self, username=None, user=None):
        if not username and not user:
            raise ValueError('Both username and user cannot be empty')

        if username:
            portal_membership = getToolByName(self.context, 'portal_membership')
            user = portal_membership.getMemberById(username)

        return user.getProperty('fullname') or user.getUserName()

    def getLogEntries(self, count=20):
        issues = [i.getObject() for i in self.context.getFilteredIssues()]

        responses = []
        for issue in issues:
            rs = issue.getFolderContents()
            responses += rs

        items = responses + issues
        
        # sort entries
        items.sort(key=getEntrySortingKey, reverse=True)

        results = []
        for item in items[:count]:
            if not callable(item.getId):
                item = item.getObject()

            base = {'title': item.title_or_id(),
                    'type': item.portal_type,
                    'author': self.getPrettyName(item.Creator())}

            if item.portal_type == 'PoiResponse':
                base.update({'date': item.modified(),
                             'timedelta': self.getTimeDelta(item.modified()),
                             'changes': item.getIssueChanges(),
                             'parent': item.aq_parent.title_or_id(),
                             'url': item.aq_parent.absolute_url(),
                             'text': item.getResponse()})

            if item.portal_type == 'PoiIssue':
                base.update({'date': item.created(),
                             'url': item.absolute_url(),
                             'timedelta': self.getTimeDelta(item.created()),
                             'text': item.getDetails()})
            
            results.append(base)
            
        return results
