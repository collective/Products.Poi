from zope.interface import Interface
from .content.issue import IIssue
from .content.tracker import ITracker

IIssue, ITracker


class IResponse(Interface):
    """Marker interface for Poi response.
    """
