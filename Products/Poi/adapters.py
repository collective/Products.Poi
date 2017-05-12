from AccessControl import getSecurityManager
from Acquisition import aq_base
from DateTime import DateTime
from collective.watcherlist.watchers import WatcherList
from DateTime import DateTime
from persistent import Persistent
from persistent.list import PersistentList
from plone.namedfile.interfaces import NotStorable
from plone.namedfile.storages import MAXCHUNKSIZE
from Products.Poi.interfaces import IIssue
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts
from zope.component import adapter
from zope.event import notify
from zope.interface import Attribute
from zope.interface import implements
from zope.interface import Interface
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent import ObjectRemovedEvent
from ZPublisher.HTTPRequest import FileUpload

import logging


logger = logging.getLogger('Products.Poi.adapters')


class IssueWatcherList(WatcherList):

    def __get_watchers(self):
        return self.context.watchers or []

    def __set_watchers(self, v):
        self.context.watchers = v

    watchers = property(__get_watchers, __set_watchers)


class TrackerWatcherList(WatcherList):

    def __get_send_emails(self):
        return self.context.notification_emails

    def __set_send_emails(self, v):
        self.context.notification_emails = v

    send_emails = property(__get_send_emails, __set_send_emails)

    def __get_extra_addresses(self):
        # Return a tuple, not a string!
        return (self.context.mailing_list, )

    def __set_extra_addresses(self, v):
        if not isinstance(v, basestring):
            # turn tuple or list into string
            v = '.'.join(v)
        self.context.setMailingList(v)

    extra_addresses = property(__get_extra_addresses, __set_extra_addresses)

    def __get_watchers(self):
        return self.context.watchers or []

    def __set_watchers(self, v):
        self.context.watchers = v

    watchers = property(__get_watchers, __set_watchers)


class IResponseContainer(Interface):
    pass


class IResponse(Interface):

    text = Attribute("Text of this response")
    rendered_text = Attribute("Rendered text (html) for caching")
    changes = Attribute("Changes made to the issue in this response.")
    creator = Attribute("Id of user making this change.")
    date = Attribute("Date (plus time) this response was made.")
    type = Attribute("Type of response (additional/clarification/reply/file).")
    mimetype = Attribute("Mime type of the response.")
    attachment = Attribute("File attachment.")

    def add_change(id, name, before, after):
        """Add change to the list of changes.
        """


class ResponseContainer(Persistent):

    implements(IResponseContainer)
    adapts(IIssue)
    ANNO_KEY = 'poi.responses'

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(self.context)
        self.__mapping = annotations.get(self.ANNO_KEY, None)
        if self.__mapping is None:
            self.__mapping = PersistentList()
            annotations[self.ANNO_KEY] = self.__mapping

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
        return key in self.__mapping

    has_key = __contains__

    def __getitem__(self, i):
        i = int(i)
        return self.__mapping.__getitem__(i)

    def __delitem__(self, item):
        self.__mapping.__delitem__(item)

    def __len__(self):
        return self.__mapping.__len__()

    def __setitem__(self, i, y):
        self.__mapping.__setitem__(i, y)

    def append(self, item):
        self.__mapping.append(item)

    def remove(self, id):
        """Remove item 'id' from the list.

        We don't actually remove the item, we just set it to None,
        so that when you edit item 3 out of 3 and someone deletes
        item 2 you are not left in the water.

        Note that we used to get passed a complete item, not an id.
        """
        id = int(id)
        self[id] = None

    def add(self, item):
        if not IResponse.providedBy(item):
            raise ValueError("IResponse interface not provided.")
        self.append(item)
        id = str(len(self))
        event = ObjectAddedEvent(item, newParent=self.context, newName=id)
        notify(event)

    def delete(self, id):
        # We need to fire an ObjectRemovedEvent ourselves here because
        # self[id].__parent__ is not exactly the same as self, which
        # in the end means that __delitem__ does not fire an
        # ObjectRemovedEvent for us.
        #
        # Also, now we can say the oldParent is the issue instead of
        # this adapter.
        event = ObjectRemovedEvent(self[id], oldParent=self.context,
                                   oldName=id)
        self.remove(id)
        notify(event)


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
        self.mimetype = ''
        self.rendered_text = None
        self.attachment = None

    def add_change(self, id, name, before, after):
        """Add a new issue change.
        """
        delta = dict(
            id=id,
            name=name,
            before=before,
            after=after)
        self.changes.append(delta)


class EmptyExporter(object):

    def __init__(self, context):
        self.context = context

    def export(self, export_context, subdir, root=False):
        return


class FileUploadStorable(object):
    # Adapted from plone.namedfile.storages.FileUploadStorable.  That one only
    # handles data from zope.publisher.browser.FileUpload.  Poi uses a hand
    # crafted, non-z3c form, so we just get an old-style FileUpload, which
    # means we need our own storage adapter.

    def store(self, data, blob):
        if not isinstance(data, FileUpload):
            raise NotStorable('Could not store data (not of "FileUpload").')

        data.seek(0)

        fp = blob.open('w')
        block = data.read(MAXCHUNKSIZE)
        while block:
            fp.write(block)
            block = data.read(MAXCHUNKSIZE)
        fp.close()
