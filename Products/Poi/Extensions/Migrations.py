try:
    from Products.contentmigration.migrator import InlineFieldActionMigrator, BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False
    
import types

from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Archetypes import transaction
from Products.CMFPlone.utils import safe_hasattr

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

    class IssueStateChangeMigrator(BaseInlineMigrator):
        src_portal_type = src_meta_type = 'PoiResponse'
        
        def migrate_issueStateChange(self):
            stateBefore = getattr(self.obj, '_issueStateBefore', None)
            stateAfter = getattr(self.obj, '_issueStateAfter', None)
            if stateBefore and stateAfter:
                issueChanges = getattr(self.obj, '_issueChanges', [])
                haveStateChange = ('review_state' in [c['id'] for c in issueChanges])
                if not haveStateChange:
                    issueChanges.append({'id' : 'review_state',
                                         'name' : 'Issue state',
                                         'before' : stateBefore,
                                         'after' : stateAfter,})
                    setattr(self.obj, '_issueChanges', issueChanges)
                delattr(self.obj, '_issueStateBefore')
                delattr(self.obj, '_issueStateAfter')

    # Attempt to do AT schema migration

    attool = getToolByName(self, 'archetype_tool')
    # Seriously, people who make these types of APIs should be shot...
    class FakeRequest:
        form = {'PoiTracker'    : True, 
                'PoiPscTracker' : True}
    attool.manage_updateSchema(REQUEST = FakeRequest())
    
    # Migrate data grid fields
    
    portal = getToolByName(self, 'portal_url').getPortalObject()
    walker = CustomQueryWalker(portal, DataFieldMigrator, query = {})
    # Need this to avoid copy errors....
    transaction.savepoint(optimistic=True)
    print >> out, "Migrating from SimpleDataGridField to DataGridField"
    walker.go()
    
    # Migrate issue state change
    
    walker = CustomQueryWalker(portal, IssueStateChangeMigrator, query = {})
    # Need this to avoid copy errors....
    transaction.savepoint(optimistic=True)
    print >> out, "Migrating issue state change storage in responses"
    walker.go()
    
    
def migrate(self):
    """Run migrations
    """
    out = StringIO()
    print >> out, "Starting Poi migration"
    beta2_rc1(self, out)
    print >> out, "Poi migrations finished"
    return out.getvalue()