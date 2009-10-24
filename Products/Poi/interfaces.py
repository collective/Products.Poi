from zope.interface import Interface


class ITracker(Interface):
    """Marker interface for Poi issue tracker."""


class IIssue(Interface):
    """Marker interface for Poi issue.
    """
    pass


class IResponse(Interface):
    """Marker interface for Poi response.
    """
    pass
