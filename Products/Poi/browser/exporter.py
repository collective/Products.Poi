import csv
import dateutil
from cStringIO import StringIO

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.Poi.adapters import IResponseContainer


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
        mt = getToolByName(self.context, 'portal_membership')
        for issue in issues:
            obj = issue.getObject()
            responsefolder = IResponseContainer(obj)
            responses = []
            for id, response in enumerate(responsefolder):
                if response is None:
                    # Has been removed.
                    continue
                responses.append({'creator': response.creator,
                                 'date': response.date})
            # the responses are in order so we just grab the last one
            if len(responses) > 0:
                last_actor = responses[-1]['creator']
                last_modified = responses[-1]['date']
            else:
                last_actor = obj.Creator()
                last_modified = obj.modified()
            actor_info = mt.getMemberInfo(last_actor)
            if actor_info and actor_info.get("fullname", None):
                last_actor = actor_info["fullname"]

            row = []
            row.append(issue.id)
            row.append(issue.Title)
            row.append(issue.target_release and
                       issue.target_release.encode('utf-8') or "")
            row.append(obj.display_area().encode('utf-8'))
            row.append(obj.display_issue_type().encode('utf-8'))
            row.append(issue.severity.encode('utf-8'))
            row.append(issue.assignee and
                       pas_member.info(
                           issue.assignee)['fullname'].encode('utf-8'))
            row.append(", ".join(sorted((y for y in issue.Subject),
                                        key=lambda x: x.lower())))
            row.append(obj.getReviewState()['title'].encode('utf-8'))
            row.append(last_actor.encode('utf-8'))
            row.append(last_modified.strftime('%Y-%m-%d %H:%M:%S'))
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
