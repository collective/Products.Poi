from zope.interface import Interface
from .content.tracker import ITracker
from .content.issue import IIssue


ITracker, IIssue


class IResponse(Interface):
    """Marker interface for Poi response.
    """
