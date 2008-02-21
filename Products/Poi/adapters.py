from zope.interface import implements
from zope.interface import Attribute
from zope.interface import Interface
from zope.component import adapts
from zope.app.container.sample import SampleContainer
from zope.annotation.interfaces import IAnnotations
from persistent import Persistent
from persistent.list import PersistentList
from Products.Poi.interfaces import IIssue
from BTrees.OOBTree import OOBTree
from AccessControl import getSecurityManager
from DateTime import DateTime


class IResponseContainer(Interface):
    pass


class IResponse(Interface):

    text = Attribute("Text of this response")
    changes = Attribute("Changes made to the issue in this response.")
    creator = Attribute("Id of user making this change.")
    date = Attribute("Date (plus time) this response was made.")

    def add_change(id, name, before, after):
        """Add change to the list of changes.
        """


class ResponseContainer(SampleContainer, Persistent):

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
            annotations[self.ANNO_KEY] = OOBTree()
            responses = annotations[self.ANNO_KEY]
        return responses

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

    def add(self, item):
        self[self._get_next_id()] = item

    def _get_next_id(self):
        try:
            number = self._SampleContainer__data.maxKey()
        except ValueError:
            # No items found yet; start at one.
            number = u"1"
        else:
            number = int(number) + 1
        return unicode(number)


class Response(Persistent):

    implements(IResponse)

    def __init__(self, text):
        self.text = text
        self.changes = PersistentList()
        sm = getSecurityManager()
        user = sm.getUser()
        self.creator = user.getId()
        self.date = DateTime()

    def add_change(self, id, name, before, after):
        """Add a new issue change.
        """
        delta = dict(
            id = id,
            name = name,
            before = before,
            after = after)
        self.changes.append(delta)
