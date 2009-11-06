from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class WatcherView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        context.toggleWatching()
        self.request.RESPONSE.redirect(context.absolute_url())
