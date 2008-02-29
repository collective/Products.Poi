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
from BTrees.OOBTree import OOBTree
from AccessControl import getSecurityManager
from DateTime import DateTime
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.container.contained import ObjectAddedEvent
from zope.app.container.interfaces import UnaddableError
from zope.event import notify


class IResponseContainer(Interface):
    pass


class IResponse(Interface):

    text = Attribute("Text of this response")
    changes = Attribute("Changes made to the issue in this response.")
    creator = Attribute("Id of user making this change.")
    date = Attribute("Date (plus time) this response was made.")
    type = Attribute("Type of response (additional/clarification/reply).")
    mime_type = Attribute("Mime type of the response.")

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
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY)

    def _newContainerData(self):
        """Construct an item-data container

        Subclasses should override this if they want different data.

        The value returned is a mapping object that also has `get`,
        `has_key`, `keys`, `items`, and `values` methods.
        """
        annotations = IAnnotations(self.context)
        mapping = annotations.get(self.ANNO_KEY, None)
        if mapping is None:
            mapping = PersistentMapping()
            mapping.data = OOBTree()
            mapping.highest = 0
            annotations[self.ANNO_KEY] = mapping
        return mapping.data

    def __contains__(self, key):
        '''See interface IReadContainer

        Taken from zope.app.container.btree.

        Reimplement this method, since has_key() returns the key if available,
        while we expect True or False.

        >>> c = ResponseContainer()
        >>> "a" in c
        False
        >>> c["a"] = 1
        >>> "a" in c
        True
        >>> "A" in c
        False
        '''
        return key in self._SampleContainer__data

    has_key = __contains__

    def __set_highest(self, highest):
        if isinstance(highest, int):
            self.__mapping.highest = highest
        else:
            raise ValueError

    def __get_highest(self):
        return self.__mapping.highest

    highest = property(__get_highest, __set_highest)

    def add(self, item):
        if not IResponse.providedBy(item):
            raise UnaddableError(self, item,
                                 "IResponse interface not provided.")
        self[unicode(self.highest + 1)] = item
        self.highest += 1

    def delete(self, id):
        # We need to fire an ObjectRemovedEvent ourselves here because
        # self[id].__parent__ is not exactly the same as self, which
        # in the end means that __delitem__ does not fire an
        # ObjectRemovedEvent for us.
        #
        # Also, now we can say the oldParent is the issue instead of
        # this adapter.
        event = ObjectRemovedEvent(self[id], oldParent=self.context, oldName=id)
        del self[id]
        notify(event)
        while unicode(self.highest) not in self and self.highest > 0:
            self.highest -= 1

    def sorted_keys(self):
        # We do not want this:
        # [u'1', u'10', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9']
        # but this:
        # [u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9', u'10']
        ints = [int(x) for x in self.keys()]
        ints.sort()
        keys = [unicode(x) for x in ints]
        return keys

    def sorted_items(self):
        return [(key, self[key]) for key in self.sorted_keys()]

    def sorted_values(self):
        return [self[key] for key in self.sorted_keys()]


class Response(Persistent):

    implements(IResponse)

    def __init__(self, text):
        self.__parent__ = self.__name__ = None
        self.text = text
        self.changes = PersistentList()
        sm = getSecurityManager()
        user = sm.getUser()
        self.creator = user.getId() or '(anonymous)'
        self.date = DateTime()
        self.type = 'additional'
        self.mime_type = ''

    def add_change(self, id, name, before, after):
        """Add a new issue change.
        """
        delta = dict(
            id = id,
            name = name,
            before = before,
            after = after)
        self.changes.append(delta)
