from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from collective.watcherlist.interfaces import IWatcherList
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class WatcherView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        # Old style
        # context.toggleWatching()
        # New style
        watchers = IWatcherList(context)
        watchers.toggle_watching()
        self.request.RESPONSE.redirect(context.absolute_url())

    def is_watching(self):
        site_url = api.portal.get().absolute_url()
        referrer = self.request.environ.get('HTTP_REFERER')
        if referrer:
            if referrer.startswith(site_url + '/'):
                alsoProvides(self.request, IDisableCSRFProtection)
        else:
            origin = self.request.environ.get('HTTP_ORIGIN')
            if origin and origin == site_url:
                alsoProvides(self.request, IDisableCSRFProtection)
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        if watchers:
            return watchers.isWatching()
        return False
