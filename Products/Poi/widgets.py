from types import StringType

from Acquisition import aq_base, aq_inner
from AccessControl import ClassSecurityInfo

from Products.Archetypes.utils import shasattr
from Products.Archetypes.Registry import registerWidget,registerPropertyType
from Products.Archetypes.Widget import ReferenceWidget


class IssueReferenceWidget(ReferenceWidget):
    _properties = ReferenceWidget._properties.copy()
    _properties.update({
        'macro': "issuereference",
        'size': '',
        'helper_js': ('issuereference.js',),
        'default_search_index': 'SearchableText',
        'show_indexes': 0,
        'available_indexes': {},
        'allow_search': 1,
        'allow_browse': 1,
        'startup_directory': '',
        'startup_directory_method': '',
        'base_query': '',
        'force_close_on_insert': 0,
        'search_catalog': 'portal_catalog',
        'allow_sorting': 0,
        'show_review_state': 0,
        'show_path': 0,
        'only_for_review_states': None,
        'image_portal_types': (),
        'image_method': None,
        'history_length': 0,
        'restrict_browsing_to_startup_directory': 0,
        'show_results_without_query': 0,
        'hide_inaccessible': 0,
        'popup_width': 500,
        'popup_height': 550,
        'popup_name': 'issuepopup',
        'browsable_types': (),
        'top_popup_helper': None,
        'bottom_popup_helper': None,
        })

    # for documentation of properties see: README.txt
    security = ClassSecurityInfo()

    security.declarePublic('getStartupDirectory')
    def getStartupDirectory(self, instance, field):
        """get widget startup directory
        """
        url_tool = instance.restrictedTraverse('@@plone_tools').url()
        basepath = '/'.join(url_tool.getRelativeContentPath(instance))
        directory = ''
        if getattr(self, 'startup_directory_method', None):
            # First check that the method exists and isn't inherited.
            method = getattr(aq_base(instance), self.startup_directory_method,
                             False)
            if method:
                # Then get the method again, but with acquisition context this
                # time:
                method = getattr(instance, self.startup_directory_method, False)
                if callable(method):
                    method = method()

                directory = method

        elif getattr(self, 'startup_directory', None):
            directory = self.startup_directory
            if not directory.startswith('/'):
                directory = '/'.join([basepath, directory])

        else:
            directory = basepath

        return directory

    security.declarePublic('getBaseQuery')
    def getBaseQuery(self, instance, field):
        """Return base query to use for content search
        """
        query = self.base_query
        if query:
            if type(query) is StringType and shasattr(instance, query):
                method = getattr(instance, query)
                results = method()
            elif callable(query):
                results = query()
            elif isinstance(query,dict):
                results = query
            else:
                raise ValueError("Wrong format for reference widget base_query parameter")
        else:
            results = {}

        # If browser browse is restricted to startup_directory
        # restrict search to it
        if getattr(self, 'restrict_browsing_to_startup_directory', False):
            startup_directory = self.getStartupDirectory(instance, field)
            try:
                startup_directory = aq_inner(instance.restrictedTraverse(startup_directory))
                results['path'] = '/'.join(startup_directory.getPhysicalPath())
            except KeyError:
                pass

        # Add portal type restrictions based on settings in field, if not part
        # of original base_query the template tries to do this, but ignores
        # allowed_types_method, which should override allowed_types
        if not results.has_key('portal_type'):
            allowed_types = getattr(field, 'allowed_types', ())
            allow_method = getattr(field, 'allowed_types_method', None)
            if allow_method is not None:
                meth = getattr(instance, allow_method)
                allowed_types = meth()

            results['portal_type'] = allowed_types# + self.browsable_types

        return results

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget
        """
        result = super(IssueReferenceWidget,
                       self).process_form(instance, field, form, empty_marker,
                                          emptyReturnsMarker, validating)
        # when removing all items from a required reference-field we get a
        # default form value of [''].  here we inject a 'custom' empty-value
        # to trigger the isempty-validator and not use the previous content of
        # the field.
        if field.required and field.multiValued and \
           not emptyReturnsMarker and result == ([''], {}):
            return [], {}

        return result

registerWidget(IssueReferenceWidget,
               title='Issue Reference Browser',
               description=('Reference widget that allows you to browse or '
                            'search the portal for objects to refer to.'),
               used_for=('Products.Archetypes.Field.ReferenceField',)
               )

registerPropertyType('default_search_index', 'string', IssueReferenceWidget)
registerPropertyType('show_index_selector', 'boolean', IssueReferenceWidget)
registerPropertyType('available_indexes', 'dictionary', IssueReferenceWidget)
registerPropertyType('allow_search', 'boolean', IssueReferenceWidget)
registerPropertyType('allow_browse', 'boolean', IssueReferenceWidget)
registerPropertyType('allow_sorting', 'boolean', IssueReferenceWidget)
registerPropertyType('startup_directory', 'string', IssueReferenceWidget)
registerPropertyType('restrict_browsing_to_startup_directory',
                     'boolean', IssueReferenceWidget)
registerPropertyType('search_catalog', 'string', IssueReferenceWidget)
registerPropertyType('image_portal_types', 'lines', IssueReferenceWidget)
registerPropertyType('image_method', 'string', IssueReferenceWidget)
registerPropertyType('force_close_on_insert',
                     'boolean', IssueReferenceWidget)
