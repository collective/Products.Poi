from StringIO import StringIO
from zope import interface
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

class IMigration(interface.Interface):
    def fix_btrees():
        """The order of inheritance of PoiPscTracker was broken at
        some point.  We need to fix BTreeFolders without `self._tree`.
        """

class Migration(BrowserView):
    def __call__(self):
        migration_id = self.request.get('migration_id')
        assert migration_id in IMigration.names(), "Unknown migration"
        return getattr(self, migration_id)()

    def fix_btrees(self):
        out = StringIO()
        catalog = getToolByName(self.context, 'portal_catalog')
        for b in catalog(portal_type='PoiPscTracker'):
            tracker = b.getObject()
            if tracker._tree is None:
                tracker._initBTrees()
                out.write('Fixed BTreeFolder at %s\n' %
                          '/'.join(tracker.getPhysicalPath()))
        return out.getvalue()
