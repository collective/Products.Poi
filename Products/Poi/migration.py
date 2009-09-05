import logging
import sets
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope import interface
from zope.publisher.browser import TestRequest
import transaction

from Products.Poi.interfaces import IIssue
from Products.Poi.adapters import Response
from Products.Poi.adapters import IResponseContainer
from Products.Poi.browser.response import Create

logger = logging.getLogger("Poi")
PROFILE_ID = 'profile-Products.Poi:default'


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


def has_old_responses(tool):
    catalog = getToolByName(tool, 'portal_catalog')
    responses = catalog.searchResults(portal_type='PoiResponse')
    if len(responses) > 0:
        logger.info("Found %s old style PoiResponses.", len(responses))
        logger.warn("Migration is needed.")
        return True
    return False


def replace_old_with_new_responses(issue):
    if not IIssue.providedBy(issue):
        return
    responses = issue.contentValues(filter={'portal_type': 'PoiResponse'})
    folder = IResponseContainer(issue)
    try:
        request = issue.REQUEST
    except AttributeError:
        # When called via prefs_install_products_form (Plone 3.3) we
        # have no REQUEST object here.  We will use a dummy then.
        request = TestRequest()
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
        except (AttributeError, KeyError):
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


def migrate_responses_alternative(context):
    """Alternative way to migrate responses.

    On big sites (like plone.org) it can be hard for the response
    migration to finish without getting a ConflictError when someone
    else is adding content at the same time.  And the normal migration
    wakes up all issues in each tracker, which is not ideal on a big
    site.

    This alternative migration can help you if a search like this
    still gives search results:
    http://plone.org/search?portal_type=PoiResponse
    """
    logger.info("Starting alternative migration of old style to new style "
                "responses.")
    catalog = getToolByName(context, 'portal_catalog')
    response_brains = catalog.searchResults(
        portal_type='PoiResponse')

    def get_parent_path(path):
        #return '/'.join(path.split('/')[:-1])
        return path[:path.rfind('/')]

    # Get a list of issues that still have one or more old style responses.
    issue_paths = sets.Set()
    logger.info("Found %d old style responses.", len(response_brains))
    for brain in response_brains:
        response_path = brain.getPath()
        issue_paths.add(get_parent_path(response_path))
    logger.info("Found %d issues with old style responses.", len(issue_paths))
    for issue_path in issue_paths:
        tracker_path = get_parent_path(issue_path)
        tracker = context.restrictedTraverse(tracker_path)
        issue = tracker.restrictedTraverse(issue_path)
        original_send_emails = tracker.getSendNotificationEmails()
        tracker.setSendNotificationEmails(False)
        logger.info("Migrating issue %s", issue_path)
        replace_old_with_new_responses(issue)
        tracker.setSendNotificationEmails(original_send_emails)
        logger.info("Committing transaction after migrating this issue.")
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
        except (AttributeError, KeyError):
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
            except (AttributeError, KeyError):
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


def run_workflow_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'workflow')
    # Run the update security on the workflow tool.
    logger.info('Updating security settings.  This may take a while...')
    wf_tool = getToolByName(context, 'portal_workflow')
    wf_tool.updateRoleMappings()
    logger.info('Done updating security settings.')


def update_tracker_managers(context):
    """Make sure all the tracker manager actually have the Manager role.

    Specifically, due to an error in the code the original creator may
    not have gotten the Manager role.
    """
    logger.info("Starting update of tracker managers.")
    catalog = getToolByName(context, 'portal_catalog')
    tracker_brains = catalog.searchResults(
        portal_type=('PoiTracker', 'PoiPscTracker'))
    logger.info("Found %s PoiTrackers.", len(tracker_brains))
    for brain in tracker_brains:
        try:
            tracker = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("AttributeError getting tracker object at %s",
                        brain.getURL())
            continue

        field = tracker.getField('managers')
        managers = field.get(tracker)
        changed = False
        for user_id in managers:
            local_roles = list(tracker.get_local_roles_for_userid(user_id))
            if not 'Manager' in local_roles:
                logger.info("User %s is tracker manager but does not have "
                            "the manager role. Fixing that now.", user_id)
                local_roles.append('Manager')
                tracker.manage_setLocalRoles(user_id, local_roles)
                changed = True
        if changed:
            logger.info("Committing after updating roles on tracker %s",
                        tracker.absolute_url())
            transaction.commit()
