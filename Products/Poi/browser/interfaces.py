from zope.interface import Interface


class IIssueFolderView(Interface):
    """Abstract a PoiTracker into a folder for issues.
    """

    def getFilteredIssues(criteria, **kwargs):
        """Get the contained issues in the given criteria.
        """

    def getIssueSearchQueryString(criteria, **kwargs):
        """Return a query string for an issue query.
        """

    def buildIssueSearchQuery(criteria, **kwargs):
        """Build canonical query for issue search.
        """

    def getMyIssues(openStates, memberId, manager):
        """Get a catalog query result set of my issues.

        So: all issues assigned to or submitted by the current user,
        with review state in openStates.

        If manager is True, you can add more states.
        """

    def getOrphanedIssues(openStates, memberId):
        """Get a catalog query result set of orphaned issues.

        Meaning: all open issues not assigned to anyone and not owned
        by the given user.
        """
