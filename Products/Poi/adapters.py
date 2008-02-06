from zope.interface import implements
from zope.interface import Attribute
from zope.interface import Interface
from zope.component import adapts
from zope.app.container.sample import SampleContainer
from zope.annotation.interfaces import IAnnotations
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from Products.Poi.interfaces import IIssue


class IResponseContainer(Interface):
    pass


class IResponse(Interface):

    text = Attribute("Text of this response")
    changes = Attribute("Changes made to the issue in this response.")

    def add_change(id, name, before, after):
        """Add change to the list of changes.
        """


class ResponseContainer(SampleContainer):

    implements(IResponseContainer)
    adapts(IIssue)
    ANNO_KEY = 'poi.responses'

    def __init__(self, context):
        self.context = context
        super(ResponseContainer, self).__init__()

    def _newContainerData(self):
        """Construct an item-data container

        Subclasses should override this if they want different data.

        The value returned is a mapping object that also has `get`,
        `has_key`, `keys`, `items`, and `values` methods.
        """
        annotations = IAnnotations(self.context)
        responses = annotations.get(self.ANNO_KEY, None)
        if responses is None:
            annotations[self.ANNO_KEY] = PersistentMapping()
            responses = annotations[self.ANNO_KEY]
        return responses

    def add(self, item):
        self[self._get_next_id()] = item

    def _get_next_id(self):
        num = len(self)
        # for safety:
        while unicode(num) in self.keys():
            num += 1
        return unicode(num)


class Response(Persistent):

    implements(IResponse)

    def __init__(self, text):
        self.text = text
        self.changes = PersistentList()
        # XXX store this: Added by  admin  on  05-02-2008 23:14

    def add_change(self, id, name, before, after):
        """Add a new issue change.
        """
        delta = dict(
            id = id,
            name = name,
            before = before,
            after = after)
        self.changes.append(delta)
