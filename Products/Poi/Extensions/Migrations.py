try:
    from Products.contentmigration.migrator import InlineFieldActionMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False
    
import types

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import transaction

def simpleDataGrid2DataGrid(obj, val, **kwargs):
    
    if type(val) not in (types.ListType, types.TupleType) or \
       len(val) < 1 or \
       type(val[0]) not in types.StringTypes:
       return val
    
    newColumns = obj.getField(kwargs['fieldName']).columns
    newValue = []
    
    for row in val:
        cols = [c.strip() for c in row.split('|')]
        newRow = {}
        for idx in range(len(newColumns)):
            newRow[newColumns[idx]] = cols[idx]
        newValue.append(newRow)
    
    return tuple(newValue)

def beta2_rc1(self, out):
    """Migrate from beta 1 to rc 1
    """
    
    if not haveContentMigrations:
        print >> out, "WARNING: Install contentmigrations to be able to migrate from beta 2 to rc 1"
        return

    class DataFieldMigrator(InlineFieldActionMigrator):
        src_portal_type = src_meta_type = ('PoiTracker', 'PoiPscTracker',)
        fieldActions = ({ 'fieldName' : 'availableAreas',
                          'transform' : simpleDataGrid2DataGrid,
                        },
                        { 'fieldName' : 'availableIssueTypes',
                          'transform' : simpleDataGrid2DataGrid,
                        },)

    attool = getToolByName(self, 'archetype_tool')

    # Seriously, people who make these types of APIs should be shot...
    class FakeRequest:
        form = {'PoiTracker'    : True, 
                'PoiPscTracker' : True}
    attool.manage_updateSchema(REQUEST = FakeRequest())
    
    portal = getToolByName(self, 'portal_url').getPortalObject()
    walker = CustomQueryWalker(portal, DataFieldMigrator, query = {})
    # Need this to avoid copy errors....
    transaction.savepoint(optimistic=True)
    print >> out, "Migrating from SimpleDataGridField to DataGridField"
    walker.go()
    
    
def migrate(self):
    """Run migrations
    """
    out = StringIO()
    print >> out, "Starting Poi migration"
    beta2_rc1(self, out)
    print >> out, "Poi migrations finished"
    return out.getvalue()