from types import ListType, TupleType
import urllib
import re

import zope.interface

from zope.component import getAdapter
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.i18nmessageid import MessageFactory
from zope.formlib import namedtemplate

from Acquisition import aq_inner
from Acquisition import aq_base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five import BrowserView

try:
    # Zope >= 2.13
    from AccessControl.security import checkPermission
    checkPermission   # pyflakes
except ImportError:
    from Products.Five.security import checkPermission

from Products.ZCTextIndex.ParseTree import ParseError

from plone.app.form._named import named_template_adapter

from Products.Archetypes.config import REFERENCE_CATALOG
from Products.CMFCore.utils import getToolByName
try:
    from plone.uuid.interfaces import IUUID
    HAS_UUID = True
except ImportError:
    HAS_UUID = False
from Products.CMFPlone.PloneBatch import Batch

from archetypes.referencebrowserwidget import utils
from archetypes.referencebrowserwidget.interfaces import IFieldRelation
from archetypes.referencebrowserwidget.interfaces import \
        IReferenceBrowserHelperView

default_popup_template = named_template_adapter(
    ViewPageTemplateFile('related_popup.pt'))

PMF = MessageFactory('plone')

class ReferenceBrowserHelperView(BrowserView):
    """ A helper view for the reference browser widget.

        The main purpose of this view is to move code out of the
        referencebrowser.pt template. This template needs to be in skins
        and can not be a view, since it is macro widget for Archetypes.
    """

    zope.interface.implements(IReferenceBrowserHelperView)

    def getFieldRelations(self, field, value=None):
        """ Query relations of a field and a context.

            Return a list of objects. If the value parameter
            is supported it needs to be a list of UIDs.
        """
        if not value:
            return queryMultiAdapter((self.context, field),
                                     interface=IFieldRelation, default=[])
        else:
            if isinstance(value, basestring):
                value = [value]
            if type(value) != ListType and type(value) != TupleType:
                return []
            catalog = getToolByName(aq_inner(self.context), REFERENCE_CATALOG)
            return [catalog.lookupObject(uid) for uid in value if uid]

    def getUidFromReference(self, ref):
        """ Helper to get UID in restricted code without having rights to
            access the object
        """
        uid = None
        if HAS_UUID:
            uid = IUUID(ref, None)
        if uid is None and hasattr(aq_base(ref), 'UID'):
            uid = ref.UID()
        return uid

    def getStartupDirectory(self, field):
        """ Return the URL to the startup directory. """
        widget = field.widget
        directory = widget.getStartupDirectory(self.context, field)
        return utils.getStartupDirectory(self.context, directory)

    def getPortalPath(self):
        tools = getMultiAdapter((self.context, self.request),
                                name='plone_tools')
        return tools.url().getPortalPath()

    def getAtURL(self):
        context = aq_inner(self.context)
        return urllib.quote('/'.join(context.getPhysicalPath()))

    def canView(self, obj):
        return checkPermission('zope2.View', obj)


class QueryCatalogView(BrowserView):

    def __call__(self, show_all=0,
                 quote_logic=0,
                 quote_logic_indexes=['SearchableText'],
                 search_catalog=None):

        results = []
        catalog = utils.getSearchCatalog(aq_inner(self.context),
                                         search_catalog)
        indexes = catalog.indexes()
        query = {}
        show_query = show_all
        second_pass = {}

        purl_tool = getToolByName(self.context, 'portal_url')
        portal_path = purl_tool.getPortalPath()

        for k, v in self.request.items():
            if v and k in indexes:
                if type(v) == str and v.strip().lower().startswith('path:'):
                    # Searching for exact path enabled! This will return the
                    # item on the specified path and all items in its subtree
                    # NOTE: Multiple spaces, slashes and/or a trailing slash in
                    # the path, while easily overlooked by users, might cause
                    # no results to be found. Let's take care of this for the
                    # convenience of the user. Besides, we need to strip
                    # 'path:' from the path string.
                    path = re.sub("/{2,}", "/", v.strip()[5:]).rstrip("/")

                    if not path.startswith("/"):
                        path = "/" + path

                    # Since we might be in a virtual-hosting environment, we
                    # need to prepend the portal path if not present yet
                    if not path.startswith(portal_path):
                        path = portal_path + path

                    d = {"path": {"query": path}}
                else:
                    if quote_logic and k in quote_logic_indexes:
                        v = utils.quotequery(v)
                    d = {k: v}
                query.update(d)
                show_query = 1

            elif k.endswith('_usage'):
                key = k[:-6]
                param, value = v.split(':')
                second_pass[key] = {param: value}
            elif k in ('sort_on', 'sort_order', 'sort_limit'):
                query.update({k: v})

        for k, v in second_pass.items():
            qs = query.get(k)
            if qs is None:
                continue
            query[k] = q = {'query': qs}
            q.update(v)

# doesn't normal call catalog unless some field has been queried
# against. if you want to call the catalog _regardless_ of whether
# any items were found, then you can pass show_all=1.

        if show_query:
            try:
                results = catalog(**query)
            except ParseError:
                pass

        return results

BORDERCOLOR = '#8cacbb'
FONTFAMILY = '"Lucida Grande", Verdana, Lucida, Helvetica, Arial, sans-serif'
DISCREETCOLOR = '#76797c'


class ReferenceBrowserPopup(BrowserView):
    """ View class of Popup window """

    has_queryresults = True
    has_brain = False
    brainuid = None
    _updated = False

    def __init__(self, context, request):
        super(ReferenceBrowserPopup, self).__init__(context, request)

        self.at_url = urllib.quote(request.get('at_url'))
        self.fieldName = request.get('fieldName')
        self.fieldRealName = request.get('fieldRealName')
        self.search_id_text = request.get('searchValueID', '')
        self.search_tag_text = request.get('searchValueTag', '')
        self.search_text = request.get('searchValue', '')

        base_props = getToolByName(aq_inner(context), 'base_properties', None)
        if base_props is not None:

            self.discreetColor = getattr(base_props, 'discreetColor',
                    DISCREETCOLOR)
        else:
            # XXX This concept has changed in Plone 4.0
            self.discreetColor = DISCREETCOLOR

    def __call__(self):
        self.update()
        return self.template()

    def update(self):
        context = aq_inner(self.context)
        self.portal_url = getToolByName(context, 'portal_url')()
        catalog = getToolByName(context, 'portal_catalog')
        at_result = catalog.searchResults(dict(path={'query': self.at_url,
                                                     'depth': 0}))
        at_brain = len(at_result) == 1 and at_result[0] or None
        if at_brain:
            self.at_obj = at_brain.getObject()
            self.has_brain = True
            self.brainuid = at_brain.UID
        else:
            self.at_obj = context.restrictedTraverse(
                    urllib.unquote(self.at_url))
        self.field = self.at_obj.Schema()[self.fieldRealName]
        self.widget = self.field.widget
        self.multiValued = int(self.field.multiValued)
        self.search_index = self.request.get('search_index',
                                             self.widget.default_search_index)
        self.request.set("SearchableText", self.search_text)
        self.request.set("Subject", self.search_tag_text)
        self.request.set("id", self.search_id_text)

        base_query = self.widget.getBaseQuery(self.at_obj, self.field)
        self.allowed_types = base_query.get('portal_type', '')
        if not self.allowed_types:
            base_query.pop('portal_type')

        if base_query.keys():
            self.request.form.update(base_query)

        # close_window needs to be int, since it is used
        # with javascript
        self.close_window = int(not self.field.multiValued or
                                self.widget.force_close_on_insert)
        popup_name = getattr(self.widget, 'popup_name', 'issuepopup')
        self.template = getAdapter(self, namedtemplate.INamedTemplate,
                                   name=popup_name or 'issuepopup')
        self.browsable_types = self.widget.browsable_types
        self._updated = True

    @property
    def search_catalog(self):
        assert self._updated
        return utils.getSearchCatalog(aq_inner(self.context),
                                      self.widget.search_catalog)

    @property
    def filtered_indexes(self):
        assert self._updated
        indexes = self.search_catalog.indexes()
        avail = self.widget.available_indexes
        return [index for index in indexes if not avail or index in avail]

    def getResult(self):
        assert self._updated
        result = []
        qc = getMultiAdapter((self.context, self.request),
                             name='issueref_querycatalog')
        if self.widget.show_results_without_query or self.search_text or \
           self.search_id_text or self.search_tag_text:
            result = (self.widget.show_results_without_query or \
                      self.search_text or self.search_id_text or \
                      self.search_tag_text) and \
                      qc(search_catalog=self.widget.search_catalog)

            self.has_queryresults = bool(result)

        elif self.widget.allow_browse:
            ploneview = getMultiAdapter((self.context, self.request),
                                        name="plone")
            folder = ploneview.getCurrentFolder()
            self.request.form['path'] = {
                              'query': '/'.join(folder.getPhysicalPath()),
                              'depth':1}
            self.request.form['portal_type'] = []
            if 'sort_on' in self.widget.base_query:
                self.request.form['sort_on'] = self.widget.base_query['sort_on']
            else:
                self.request.form['sort_on'] = 'getObjPositionInParent'

            result = qc(search_catalog=self.widget.search_catalog)
        else:
            result = []
        b_size = int(self.request.get('b_size', 20))
        b_start = int(self.request.get('b_start', 0))

        return Batch(result, b_size, b_start, orphan=1)

    def breadcrumbs(self, startup_directory=None):
        assert self._updated
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        bc_view = context.restrictedTraverse('@@breadcrumbs_view')
        crumbs = bc_view.breadcrumbs()

        if not self.widget.restrict_browsing_to_startup_directory:
            newcrumbs = [{'Title': PMF('Home'),
                          'absolute_url': self.genRefBrowserUrl(
                                portal_state.navigation_root_url())}]
        else:
            # display only crumbs into startup directory
            startup_dir_url = startup_directory or \
                utils.getStartupDirectory(context,
                        self.widget.getStartupDirectory(context, self.field))
            newcrumbs = []
            crumbs = [c for c in crumbs \
                             if c['absolute_url'].startswith(startup_dir_url)]

        for c in crumbs:
            c['absolute_url'] = self.genRefBrowserUrl(c['absolute_url'])
            newcrumbs.append(c)

        return newcrumbs

    def genRefBrowserUrl(self, urlbase):
        assert self._updated
        return "%s/%s?fieldName=%s&fieldRealName=%s&at_url=%s" % (
       urlbase, self.__name__, self.fieldName, self.fieldRealName, self.at_url)

    def getUid(self, item):
        assert self._updated
        return getattr(aq_base(item), 'UID', None)

    def isNotSelf(self, item):
        assert self._updated

        def safe_get_object(item):
            """ Return an object from the catalog, if it exists """
            try:
                return item.getObject()
            except AttributeError:
                return None

        return self.has_brain and self.getUid(item) != self.brainuid or \
               safe_get_object(item) != self.at_obj

    def isReferencable(self, item):
        assert self._updated
        item_referenceable = not self.allowed_types or \
            item.portal_type in self.allowed_types
        filter_review_states = self.widget.only_for_review_states is not None
        review_state_allows = True
        if filter_review_states:
            review_state_allows = item.review_state in \
                (self.widget.only_for_review_states or ())
        return self.getUid(item) and item_referenceable and \
               review_state_allows and self.isNotSelf(item)

    def isBrowsable(self, item):
        if not self.browsable_types:
            return item.is_folderish
        else:
            return item.portal_type in self.browsable_types

    def title_or_id(self, item):
        assert self._updated
        item = aq_base(item)
        return getattr(item, 'Title', '') or getattr(item, 'getId', '')

    def preview_url(self, item):
        portal_properties = getMultiAdapter((self.context, self.request),
                                            name=u'plone_tools').properties()
        site_properties = portal_properties.site_properties
        types_use_view = site_properties.typesUseViewActionInListings
        if item.portal_type in types_use_view:
            return item.getURL()+'/view'
        return item.getURL()
