from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from collective.watcherlist.interfaces import IWatcherList


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
        context = aq_inner(self.context)
        watchers = IWatcherList(context)
        return watchers.isWatching()
