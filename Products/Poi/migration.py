import logging
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope import interface
import transaction

from Products.Poi.interfaces import IIssue
from Products.Poi.adapters import Response
from Products.Poi.adapters import IResponseContainer
from Products.Poi.browser.response import Create

logger = logging.getLogger("Poi")


class IMigration(interface.Interface):

    def fix_btrees():
        """The order of inheritance of PoiPscTracker was broken at
        some point.  We need to fix BTreeFolders without `self._tree`.
        """


class Migration(BrowserView):

    def __call__(self):
        migration_id = self.request.get('migration_id')
        assert migration_id in IMigration.names(), "Unknown migration"
        return getattr(self, migration_id)()

    def fix_btrees(self):
        out = StringIO()
        catalog = getToolByName(self.context, 'portal_catalog')
        for b in catalog(portal_type='PoiPscTracker'):
            tracker = b.getObject()
            if tracker._tree is None:
                tracker._initBTrees()
                out.write('Fixed BTreeFolder at %s\n' %
                          '/'.join(tracker.getPhysicalPath()))
        return out.getvalue()


def replace_old_with_new_responses(issue):
    if not IIssue.providedBy(issue):
        return
    responses = issue.contentValues(filter={'portal_type': 'PoiResponse'})
    folder = IResponseContainer(issue)
    request = issue.REQUEST
    createview = Create(issue, request)
    path = '/'.join(issue.getPhysicalPath())
    logger.debug("Migrating %s responses for issue at %s",
                 len(responses), path)
    if not responses:
        return
    for old_response in responses:
        field = old_response.getField('response')
        text = field.getRaw(old_response)
        new_response = Response(text)
        new_response.mimetype = field.getContentType(old_response)
        new_response.creator = old_response.Creator()
        new_response.date = old_response.CreationDate()
        new_response.type = createview.determine_response_type(new_response)
        changes = old_response.getIssueChanges()
        for change in changes:
            new_response.add_change(**change)
        attachment_field = old_response.getField('attachment')
        attachment = attachment_field.getRaw(old_response)
        if attachment.get_size() > 0:
            new_response.attachment = attachment
        folder.add(new_response)
        issue._delObject(old_response.getId())
    # This seems a good time to reindex the issue for good measure.
    issue.reindexObject()


def migrate_responses(context):
    logger.info("Starting migration of old style to new style responses.")
    catalog = getToolByName(context, 'portal_catalog')
    tracker_brains = catalog.searchResults(
        portal_type=('PoiTracker', 'PoiPscTracker'))
    logger.info("Found %s PoiTrackers.", len(tracker_brains))
    for brain in tracker_brains:
        try:
            tracker = brain.getObject()
        except AttributeError:
            logger.warn("AttributeError getting tracker object at %s",
                        brain.getURL())
            continue
        # We definitely do not want to send any emails for responses
        # added or removed during this migration.
        original_send_emails = tracker.getSendNotificationEmails()
        tracker.setSendNotificationEmails(False)
        logger.info("Migrating %s issues in tracker %s",
                    len(tracker.contentIds()), tracker.absolute_url())
        for issue in tracker.contentValues():
            replace_old_with_new_responses(issue)
        tracker.setSendNotificationEmails(original_send_emails)
        # We do a transaction commit here.  Otherwise on large sites
        # (say plone.org) it may be virtually impossible to finish
        # this very big migration.
        logger.info("Committing transaction after migrating this tracker.")
        transaction.commit()


def migrate_workflow_changes(context):
    """Migrate workflow changes from ids to titles.

    When a response changes the workflow state of an issue, this
    change is recorded in that response.  This used to be done by
    storing review state ids.  Currently this is done by storing
    review state titles.  Friendlier for the end user and translatable
    to boot.  This migration finds responses with review state ids in
    them and turns them into titles.
    """
    logger.info("Starting migration of workflow changes.")
    catalog = getToolByName(context, 'portal_catalog')
    wftool = getToolByName(context, 'portal_workflow')

    def get_state_title(state_id):
        # This neatly returns the input when there is no such review
        # state id, which happens when the 'state_id' is already a
        # title.
        return wftool.getTitleForStateOnType(state_id, 'PoiIssue')

    issue_brains = catalog.searchResults(portal_type='PoiIssue')
    logger.info("Found %s PoiIssues.", len(issue_brains))
    fixed = 0
    for brain in issue_brains:
        try:
            issue = brain.getObject()
        except AttributeError:
            logger.warn("AttributeError getting issue object at %s",
                        brain.getURL())
            continue
        folder = IResponseContainer(issue)
        made_changes = False
        for response in folder:
            for change in response.changes:
                #def add_change(self, id, name, before, after):
                if change['id'] != 'review_state':
                    continue
                before = get_state_title(change['before'])
                if change['before'] != before:
                    made_changes = True
                    change['before'] = before
                change['after'] = get_state_title(change['after'])
        if made_changes:
            fixed += 1
            if fixed % 100 == 0:
                logger.info("Committing transaction after fixing "
                            "%s PoiIssues; still busy... " % fixed)
                transaction.commit()
    logger.info("Migration completed.  %s PoiIssues needed fixing.", fixed)


def fix_descriptions(context):
    """Fix issue Descriptions.

    In revision 53855 a change was made that caused the Description
    field of issues that were first strings to now possibly turn into
    unicode.  That fixed this issue:
    http://plone.org/products/poi/issues/135

    But as stated at the bottom of that issue, this can give a
    UnicodeEncodeError when changing the issue or adding a response to
    it.  The Description string that is in the catalog brain is
    compared to the unicode Description from the object and this fails
    when the brain Description has non-ascii characters.

    A good workaround is to clear and rebuild the catalog.  But
    running this upgrade step also fixes it.
    """
    logger.info("Start fixing issue descriptions.")
    catalog = getToolByName(context, 'portal_catalog')
    brains = catalog.searchResults(portal_type='PoiIssue')
    logger.info("Found %s PoiIssues.", len(brains))
    fixed = 0
    for brain in brains:
        if isinstance(brain.Description, str):
            try:
                issue = brain.getObject()
            except AttributeError:
                logger.warn("AttributeError getting issue object at %s",
                            brain.getURL())
                continue
            if isinstance(issue.Description(), unicode):
                logger.debug("Un/reindexing PoiIssue %s", brain.getURL())
                # This is the central point really: directly
                # reindexing this issue can fail if the description
                # has non-ascii characters.  So we unindex it first.
                catalog.unindexObject(issue)
                catalog.reindexObject(issue)
                fixed += 1
                if fixed % 100 == 0:
                    logger.info("Committing transaction after fixing "
                                "%s PoiIssues; still busy... " % fixed)
                    transaction.commit()
    logger.info("Fix completed.  %s PoiIssues needed fixing.", fixed)
