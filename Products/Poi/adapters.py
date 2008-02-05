from zope.interface import implements
from zope.interface import Attribute
from zope.interface import Interface
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from persistent import Persistent
from persistent.list import PersistentList
from Products.Poi.interfaces import IIssue


class IResponseContainer(Interface):

    responses = Attribute("Responses in this container")

    def add_response(response):
        """Add a response.
        """

    def remove_response(response):
        """Remove a response.
        """


class IResponse(Interface):

    text = Attribute("Text of this response")
    changes = Attribute("Changes made to the issue in this response.")

    def add_change(id, name, before, after):
        """Add change to the list of changes.
        """


class ResponseContainer(object):

    implements(IResponseContainer)
    adapts(IIssue)
    ANNO_KEY = 'poi.responses'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self.responses = annotations.get(self.ANNO_KEY, None)
        if self.responses is None:
            annotations[self.ANNO_KEY] = PersistentList()
            self.responses = annotations[self.ANNO_KEY]

    def add_response(self, response):
        self.responses.append(response)

    def remove_response(self, response):
        self.responses.remove(response)


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
