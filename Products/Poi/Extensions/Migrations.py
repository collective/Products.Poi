try:
    from Products.contentmigration.migrator import InlineFieldActionMigrator, BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False
    
import types
from StringIO import StringIO

from Acquisition import aq_base
import transaction

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.BaseUnit import BaseUnit
from Products.CMFPlone.utils import safe_hasattr

from Products.Poi.content import PoiTracker 
from Products.Poi.config import *


def simpleDataGrid2DataGrid(obj, val, **kwargs):
    
    if type(val) not in (types.ListType, types.TupleType) or \
       len(val) < 1 or \
       type(val[0]) not in types.StringTypes:
       return val
    
    newColumns = kwargs['newColumns']
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
                
    class DetailsMigrator(BaseInlineMigrator):
        src_portal_type = src_meta_type = 'PoiIssue'
        
        def migrate_details(self):
            overview = getattr(aq_base(self.obj), 'description', None)
            if overview is not None:
                try:
                    delattr(aq_base(self.obj), 'description')
                except (AttributeError, KeyError,):
                    pass
                if overview:
                    overview = overview.transform(self.obj, 'text/plain')

            detailsBase = self.obj.getField('details').get(self.obj, raw=True)
            mimetype = detailsBase.getContentType()
            
            if mimetype in ('text/plain', 'text/structured', 'text/reststructured', 'text/x-web-intelligent',):
                self.obj.setDetails(overview + '\n\n' + detailsBase.getRaw(), mimetype='text/x-web-intelligent')
            else:
                details = detailsBase.transform(self.obj, 'text/html')
                if details is None:
                    details = ''
                transforms = getToolByName(self.obj, 'portal_transforms')
                converted = transforms.convertTo('text/x-web-intelligent', details, context=self.obj, mimetype='text/html').getData()
                if overview:
                    converted = overview + '\n\n' + converted
                self.obj.setDetails(converted, mimetype='text/x-web-intelligent')
    
    class StepsToReproduceMigrator(BaseInlineMigrator):
        src_portal_type = src_meta_type = 'PoiIssue'
        
        def migrate_steps(self):
            val = getattr(aq_base(self.obj), 'steps', None)
            if val is None or \
                type(val) not in (types.ListType, types.TupleType):
                return
            newVal = '\n'.join(val)
            self.obj.steps = BaseUnit('steps', file=newVal, instance=self.obj, mimetype='text/x-web-intelligent')
    
    class ResponseMigrator(BaseInlineMigrator):
        src_portal_type = src_meta_type = 'PoiResponse'
        
        def migrate_response(self):
            responseBase = self.obj.getResponse(raw=True)
            mimetype = responseBase.getContentType()
            
            if mimetype in ('text/plain', 'text/structured', 'text/reststructured', 'text/x-web-intelligent',):
                self.obj.setResponse(responseBase.getRaw(), mimetype='text/x-web-intelligent')
            else:
                response = responseBase.transform(self.obj, 'text/html')
                transforms = getToolByName(self.obj, 'portal_transforms')
                converted = transforms.convertTo('text/x-web-intelligent', response, context=self.obj, mimetype='text/html').getData()
                self.obj.setResponse(converted, mimetype='text/x-web-intelligent')
        
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
    transaction.savepoint(optimistic=True)
    print >> out, "Migrating from SimpleDataGridField to DataGridField"
    walker.go(newColumns = PoiTracker.schema['availableAreas'].columns)
    
    # Migrate issue state change
    walker = CustomQueryWalker(portal, IssueStateChangeMigrator, query = {})
    transaction.savepoint(optimistic=True)
    print >> out, "Migrating issue state change storage in responses"
    walker.go()
    
    # Migrate to plain-text if html isn't allowed but plain-text is
    if 'text/html' not in ISSUE_MIME_TYPES and 'text/x-web-intelligent' in ISSUE_MIME_TYPES:
        # Migrate issue details field
        walker = CustomQueryWalker(portal, DetailsMigrator, query = {})
        transaction.savepoint(optimistic=True)
        print >> out, "Migrating issue details field to text"
        walker.go()
    
        # Migrate issue steps-to-reproduce field
        walker = CustomQueryWalker(portal, StepsToReproduceMigrator, query = {})
        transaction.savepoint(optimistic=True)
        print >> out, "Migrating issue steps-to-reproduce to text"
        walker.go()
    
        # Migrate response field
        walker = CustomQueryWalker(portal, ResponseMigrator, query = {})
        transaction.savepoint(optimistic=True)
        print >> out, "Migrating response text field to text"
        walker.go()
    
def migrate(self):
    """Run migrations
    """
    out = StringIO()
    print >> out, "Starting Poi migration"
    beta2_rc1(self, out)
    print >> out, "Poi migrations finished"
    return out.getvalue()
