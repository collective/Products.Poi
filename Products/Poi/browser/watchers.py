from collective.watcherlist.interfaces import IWatcherList
from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class WatcherView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        # Old style
        context.toggleWatching()
        # New style
        watchers = IWatcherList(context)
        watchers.toggle_watching()
        self.request.RESPONSE.redirect(context.absolute_url())
