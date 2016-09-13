import csv
import dateutil
from cStringIO import StringIO

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName


from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser as BaseUnrestrictedUser


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """
    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()


def execute_under_special_role(portal, role, function, *args, **kwargs):
    """ Execute code under special role privileges.

    Example how to call::

        execute_under_special_role(portal, "Manager",
            doSomeNormallyNotAllowedStuff,
            source_folder, target_folder)


    @param portal: Reference to ISiteRoot object whose access controls we are
                    using

    @param function: Method to be called with special privileges

    @param role: User role for the security context when calling the
                 privileged code; e.g. "Manager".

    @param args: Passed to the function

    @param kwargs: Passed to the function
    """

    sm = getSecurityManager()

    try:
        try:
            # Clone the current user and assign a new role.
            # Note that the username (getId()) is left in exception
            # tracebacks in the error_log,
            # so it is an important thing to store.
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', [role], ''
                )

            # Wrap the user in the acquisition context of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)

            # Call the function
            return function(*args, **kwargs)

        except:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)


class CSVExport(BrowserView):
    """ view to produce the CSV exports
    """

    def __call__(self):
        context = aq_inner(self.context)
        encoding = self.request.get('encoding')
        issuefolder = context.restrictedTraverse('@@issuefolder')
        pas_member = context.restrictedTraverse('@@pas_member')

        issues = issuefolder.getFilteredIssues(self.request)
        buffer = StringIO()

        writer = csv.writer(buffer)
        header = [
            '#',
            'Title',
            'Target',
            'Area',
            'Type',
            'Severity',
            'Assignee',
            'Tags',
            'State',
            'Last modified by',
            'Last modified by date/time',
            'Version',
            'Submitted by',
            'Submitted date/time',
        ]
        writer.writerow(header)
        # to get the previous person who changed something
        # we need to get workflow and revision history
        rt = getToolByName(context, "portal_repository", None)
        workflow = getToolByName(context, 'portal_workflow')
        mt = getToolByName(self.context, 'portal_membership')
        for issue in issues:
            obj = issue.getObject()
            review_history = execute_under_special_role(
                context,
                'Manager',
                workflow.getInfoFor,
                obj,
                'review_history')
            version_history = []
            history = rt.getHistoryMetadata(obj)
            if history:
                retrieve = history.retrieve
                for i in xrange(
                        history.getLength(countPurged=False)-1, -1, -1):
                    vdata = retrieve(i, countPurged=False)
                    meta = vdata["metadata"]["sys_metadata"]
                    info = dict(
                        actor=meta["principal"],
                        time=meta["timestamp"]
                    )
                    version_history.append(info)
            full_history = review_history + version_history
            full_history.sort(key=lambda x: x["time"], reverse=True)
            last_actor = full_history[0]["actor"]
            actor_info = mt.getMemberInfo(last_actor)
            if actor_info and actor_info.get("fullname", None):
                last_actor = actor_info["fullname"]

            row = []
            row.append(issue.id)
            row.append(issue.Title)
            row.append(issue.target_release and issue.target_release.encode('utf-8') or "")
            row.append(obj.display_area().encode('utf-8'))
            row.append(obj.display_issue_type().encode('utf-8'))
            row.append(issue.severity.encode('utf-8'))
            row.append(issue.assignee and pas_member.info(issue.assignee)['fullname'].encode('utf-8'))
            row.append(", ".join(sorted((y for y in issue.Subject), key=lambda x: x.lower())))
            row.append(obj.getReviewState()['title'].encode('utf-8'))
            row.append(last_actor.encode('utf-8'))
            row.append(dateutil.parser.parse(
                issue.modified.ISO()).strftime('%Y-%m-%d %H:%M:%S')
            )
            row.append(issue.release and issue.release.encode('utf-8') or "")
            row.append(
                pas_member.info(issue.Creator)['name_or_id'].encode('utf-8'))
            row.append(dateutil.parser.parse(
                issue.CreationDate).strftime('%Y-%m-%d %H:%M:%S')
            )
            writer.writerow(row)
        value = buffer.getvalue()
        value = unicode(value, "utf-8").encode("iso-8859-1", "replace")

        if not encoding:
            encoding = 'UTF-8'
        self.request.response.setHeader('Content-type',
                                        'text/csv;charset='+encoding)
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename=export.csv')

        return value
