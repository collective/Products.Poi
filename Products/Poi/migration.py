from Acquisition import aq_parent
from collective.watcherlist.interfaces import IWatcherList
from plone import api
from plone.app.contenttypes.migration.migration import migrateCustomAT
from plone.namedfile import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from Products.CMFFormController.FormAction import FormActionKey
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_unicode
from Products.Poi.adapters import IResponseContainer, ResponseContainer
from Products.Poi.utils import normalize_filename
from ZODB.POSException import ConflictError
from zope.annotation.interfaces import IAnnotations
from zope.container.interfaces import INameChooser
from zope.schema._bootstrapinterfaces import ConstraintNotSatisfied

import logging
import transaction


logger = logging.getLogger("Poi")
PROFILE_ID = 'profile-Products.Poi:default'


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
            logger.warn("AttributeError or KeyError getting tracker object at "
                        "%s", brain.getURL())
            continue
        folder = IResponseContainer(issue)
        made_changes = False
        for response in folder:
            for change in response.changes:
                # def add_change(self, id, name, before, after):
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


def run_workflow_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'workflow')
    # Run the update security on the workflow tool.
    logger.info('Updating security settings.  This may take a while...')
    wf_tool = getToolByName(context, 'portal_workflow')
    wf_tool.updateRoleMappings()
    logger.info('Done updating security settings.')


def update_tracker_managers(context, testing=False):
    """Make sure all managers of a tracker get the TrackerManager role.

    We used to give users in the 'managers' field of a tracker the
    local Manager role.  Now we give them the new TrackerManager role.
    In this upgrade step we remove the local Manager role from all
    users.  Instead we give them the TrackerManager role.  This might
    give a few 'false positives', where a user has been intentionally
    given the local Manager role and will now lose it.  That can't be
    helped and is not expected to be a big problem.

    If testing is True, do not commit; this avoids some problems when
    running the tests.
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
            logger.warn("AttributeError or KeyError getting tracker object at "
                        "%s", brain.getURL())
            continue

        field = tracker.getField('managers')
        managers = field.get(tracker)
        tracker_changed = False
        for user_id in managers:
            user_changed = False
            local_roles = list(tracker.get_local_roles_for_userid(user_id))
            if 'Manager' in local_roles:
                logger.info("Removing local Manager role from user %s.",
                            user_id)
                local_roles.remove('Manager')
                user_changed = True
            if 'TrackerManager' not in local_roles:
                logger.info("Giving user %s TrackerManager role.", user_id)
                local_roles.append('TrackerManager')
                user_changed = True
            if user_changed:
                tracker.manage_setLocalRoles(user_id, local_roles)
                tracker_changed = True
        if tracker_changed and not testing:
            logger.info("Committing after updating roles on tracker %s",
                        tracker.absolute_url())
            transaction.commit()


def remove_form_controller_action(context):
    """Remove our action from the portal_form_controller.

    We used to add the poi_issue_post action (a skin script) to the
    validate_integrity script.  Now we have registered an event
    handler instead so the action is no longer needed.  And we have
    removed the skin script, so we must remove the action as otherwise
    anyone submitting a new issue will get an error.
    """
    controller = getToolByName(context, 'portal_form_controller')
    action_key = FormActionKey('validate_integrity', 'success', 'PoiIssue', '')
    try:
        action = controller.actions.get(action_key)
    except KeyError:
        logger.info("Action for validate_integrity not found; ignoring.")
        return
    if action.getActionArg() != 'string:poi_issue_post':
        logger.info("Expected action argument 'string:poi_issue_post' for "
                    "successfull validate_integrity on PoiIssue; found %r "
                    "instead; ignoring.", action.getActionArg())
        return
    try:
        controller.actions.delete(action_key)
    except (ConflictError, KeyboardInterrupt):
        raise
    except Exception, exc:
        # This way of removing an action is yucky; I wonder how many
        # things can go wrong; let's inform the user.
        url = controller.absolute_url() + '/manage_formActionsForm'
        error = ("Exception while removing action poi_issue_post on "
                 "validate_integrity. Please go to %s and remove it manually. "
                 "Original exception was: %r" % (url, exc))
        raise Exception(error)
    else:
        logger.info("Removed action poi_issue_post from validate_integrity.")


def run_rolemap_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'rolemap')


def run_sharing_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'sharing')


def run_types_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'typeinfo')


def purge_workflow_scripts(context):
    """Remove reference to old workflow scripts.

    We used to have some external methods hooked up to the issue
    workflow, but this is now done with events.  Having the scripts
    mentioned in the ZMI does not seem to cause problems, but it is
    cleaner to remove them, as we do not need them.  Also, a workflow
    export and import would fail.
    """
    wf_tool = getToolByName(context, 'portal_workflow')
    wf_id = 'poi_issue_workflow'
    bad_scripts = ('sendInitialEmail', 'sendResolvedMail')
    wf = wf_tool.getWorkflowById(wf_id)
    for script_name in bad_scripts:
        if script_name in wf.scripts.objectIds():
            wf.scripts._delObject(script_name)
            logger.info('Removed script %s from %s', script_name, wf_id)


def run_javascript_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'jsregistry')


def migrate_tracker_watchers(context):
    """Migrate tracker watchers.

    Watchers of a tracker were first stored in annotations, but should
    now be stored in a LinesField.
    """
    logger.info("Starting update of tracker watchers.")
    catalog = getToolByName(context, 'portal_catalog')
    tracker_brains = catalog.searchResults(
        portal_type=('PoiTracker', 'PoiPscTracker'))
    logger.info("Found %s PoiTrackers.", len(tracker_brains))
    for brain in tracker_brains:
        try:
            tracker = brain.getObject()
        except (AttributeError, KeyError):
            logger.warn("AttributeError or KeyError getting tracker object at "
                        "%s", brain.getURL())
            continue

        watchers = IWatcherList(tracker)
        # We would want to check watchers.__mapping, but that fails.
        # watchers._WatcherList__mapping would work, but it looks
        # suspicious to me.  So let's get the annotations.
        annotations = IAnnotations(tracker)
        mapping = annotations.get(watchers.ANNO_KEY, None)
        if not mapping:
            continue
        try:
            old_value = mapping['watchers']
        except KeyError:
            continue
        logger.info("Setting watchers of tracker at %s: %r",
                    tracker.absolute_url(), old_value)
        tracker.setWatchers(old_value)
        del mapping['watchers']


def recook_resources(context):
    context.portal_javascripts.cookResources()
    context.portal_css.cookResources()


def migrate_response_attachments_to_blobstorage(context):
    logger.info('Migrating response attachments to blob storage.')
    catalog = getToolByName(context, 'portal_catalog')
    already_migrated = 0
    migrated = 0
    for brain in catalog.unrestrictedSearchResults(portal_type='PoiIssue'):
        path = brain.getPath()
        try:
            issue = brain.getObject()
        except (AttributeError, ValueError, TypeError):
            logger.warn('Error getting object from catalog for path %s', path)
            continue
        folder = IResponseContainer(issue)
        for id, response in enumerate(folder):
            if response is None:
                # Has been removed.
                continue
            attachment = response.attachment
            if attachment is None:
                continue
            if isinstance(attachment, NamedBlobFile):
                # Already migrated
                logger.debug('Response %d already migrated, at %s.', id, path)
                already_migrated += 1
                continue
            content_type = getattr(attachment, 'content_type', '')
            filename = getattr(attachment, 'filename', '')
            if not filename and hasattr(attachment, 'getId'):
                filename = attachment.getId()
            data = attachment.data
            # Data can be 'nested' in OFS.Image.Pdata.
            if base_hasattr(data, 'data'):
                data = data.data
            filename = safe_unicode(filename)
            try:
                blob = NamedBlobFile(
                    data, contentType=content_type, filename=filename)
            except ConstraintNotSatisfied:
                # Found in live data: a filename that includes a newline...
                logger.info('Trying to normalize filename %s', filename)
                filename = normalize_filename(filename, context.REQUEST)
                logger.info('Normalize to %s', filename)
                blob = NamedBlobFile(
                    data, contentType=content_type, filename=filename)
            response.attachment = blob
            logger.debug('Response %d migrated, at %s.', id, path)
            migrated += 1

    logger.info('Migrated %d response attachments to blobs. '
                '%d already migrated.', migrated, already_migrated)


def migrate_issue_attachments_to_blobstorage(context):
    from plone.app.blob.migrations import migrate
    logger.info('Migrating to blob attachments for issues. '
                'This can take a long time...')
    # Technically, the plone.app.blob migration says it is only for non blob
    # fields that are still in the schema but are overridden using
    # archetypes.schemaextender with a blob field with the same name.  But it
    # seems to go fine for Issues where we have simply changed the schema
    # directly.  The getters of a BlobFileField and normal FileField don't
    # differ that much.
    migrate(context, 'PoiIssue')
    logger.info("Done migrating to blob attachment for issues.")


def datagrid_field_migrator(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Change the dict key 'id' to 'short_name'
    """
    field = src_obj.getField(src_fieldname)
    at_value = field.get(src_obj)
    for val in at_value:
        val['short_name'] = val['id']
        del val['id']
    setattr(dst_obj, dst_fieldname, at_value)


def merge_managers(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Combine managers and technicians into a single field
    """
    technicians = src_obj.getField(src_fieldname).get(src_obj)
    managers = src_obj.getField('managers').get(src_obj)
    dx_value = list(set(technicians + managers))
    setattr(dst_obj, dst_fieldname, dx_value)


def return_list(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Returns value as a list
    """
    field = src_obj.getField(src_fieldname).get(src_obj)
    setattr(dst_obj, dst_fieldname, [x for x in field])


def return_blank(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """If field is set to '(UNASSIGNED)', make it blank
    """
    field = src_obj.getField(src_fieldname).get(src_obj)
    if field == '(UNASSIGNED)':
        setattr(dst_obj, dst_fieldname, None)
    else:
        setattr(dst_obj, dst_fieldname, field)


def move_attachments(src_obj, dst_obj, src_fieldname, dst_fieldname):
    """Take attachments and responses from the field, add as items
       inside the issue
    """
    field = src_obj.getField(src_fieldname).get(src_obj)
    if field.data:
        if hasattr(field, 'filename'):
            fname = field.filename
        elif hasattr(field, 'title'):
            fname = field.title
        else:
            fname = "Attachment"
        file_obj = src_obj.getAttachment()
        filename = safe_unicode(fname)
        exts = ['jpg', 'jpeg', 'gif', 'png', 'tiff']
        if any(ext in filename for ext in exts):
            new_obj = api.content.create(
                container=dst_obj,
                type='Image',
                title=filename,
                id="tmp",
                file=file_obj.data)
        else:
            new_obj = api.content.create(
                container=dst_obj,
                type='File',
                title=filename,
                id="tmp",
                file=file_obj.data)
        transaction.commit()
        oid = INameChooser(dst_obj).chooseName(fname, new_obj)
        new_obj.setId(oid)
        new_obj.setFilename(oid)
        new_obj.content_type = file_obj.getContentType()
        new_obj.reindexObject()
    atresponses = IResponseContainer(src_obj, None)
    dxissue = ResponseContainer(dst_obj)
    for response in atresponses:
        if not response:
            continue
        atch = response.attachment
        if not atch:
            dxissue.add(response)
            continue

        if atch.title:
            fname = atch.title
        else:
            fname = "Attachment"
        filename = safe_unicode(fname)
        exts = ['jpg', 'jpeg', 'gif', 'png', 'tiff']
        if any(ext in filename for ext in exts):
            new_obj = api.content.create(
                container=dst_obj,
                type='Image',
                title=filename,
                id="tmp",
                file=atch.data)
        else:
            new_obj = api.content.create(
                container=dst_obj,
                type='File',
                title=filename,
                id="tmp",
                file=atch.data)
        transaction.commit()
        oid = INameChooser(dst_obj).chooseName(fname, new_obj)
        new_obj.setId(oid)
        new_obj.setFilename(oid)
        new_obj.content_type = atch.getContentType()
        new_obj.reindexObject()
        atch.id = oid
        dxissue.add(response)


def dexterity_migration(context):
    # first run default profile to make sure DX types are available
    portal_setup = api.portal.get_tool('portal_setup')
    portal_setup.runAllImportStepsFromProfile("profile-Products.Poi:default")

    # Tracker
    fields_mapping = (
        {'AT_field_name': 'title',
         'DX_field_name': 'title',
         },
        {'AT_field_name': 'description',
         'DX_field_name': 'description',
         },
        {'AT_field_name': 'helpText',
         'DX_field_name': 'help_text',
         },
        {'AT_field_name': 'availableAreas',
         'DX_field_name': 'available_areas',
         'field_migrator': datagrid_field_migrator
         },
        {'AT_field_name': 'availableIssueTypes',
         'DX_field_name': 'available_issue_types',
         'field_migrator': datagrid_field_migrator
         },
        {'AT_field_name': 'availableSeverities',
         'DX_field_name': 'available_severities',
         },
        {'AT_field_name': 'defaultSeverity',
         'DX_field_name': 'default_severity',
         },
        {'AT_field_name': 'availableReleases',
         'DX_field_name': 'available_releases',
         },
        {'AT_field_name': 'technicians',
         'DX_field_name': 'assignees',
         'field_migrator': merge_managers
         },
        {'AT_field_name': 'watchers',
         'DX_field_name': 'watchers',
         'field_migrator': return_list
         },
        {'AT_field_name': 'sendNotificationEmails',
         'DX_field_name': 'notification_emails',
         },
        {'AT_field_name': 'mailingList',
         'DX_field_name': 'mailing_list',
         },
        {'AT_field_name': 'svnUrl',
         'DX_field_name': 'repo_url',
         },
    )
    migrateCustomAT(
        fields_mapping,
        src_type='PoiTracker',
        dst_type='Tracker')

    # Issue
    fields_mapping = (
        {'AT_field_name': 'title',
         'DX_field_name': 'title',
         },
        {'AT_field_name': 'release',
         'DX_field_name': 'release',
         'field_migrator': return_blank
         },
        {'AT_field_name': 'details',
         'DX_field_name': 'details',
         },
        {'AT_field_name': 'steps',
         'DX_field_name': 'steps',
         },
        {'AT_field_name': 'attachment',
         'DX_field_name': 'attachment',
         'field_migrator': move_attachments
         },
        {'AT_field_name': 'area',
         'DX_field_name': 'area',
         },
        {'AT_field_name': 'issueType',
         'DX_field_name': 'issue_type',
         },
        {'AT_field_name': 'severity',
         'DX_field_name': 'severity',
         },
        {'AT_field_name': 'targetRelease',
         'DX_field_name': 'target_release',
         'field_migrator': return_blank
         },
        {'AT_field_name': 'responsibleManager',
         'DX_field_name': 'assignee',
         'field_migrator': return_blank
         },
        {'AT_field_name': 'contactEmail',
         'DX_field_name': 'contact_email',
         },
        {'AT_field_name': 'watchers',
         'DX_field_name': 'watchers',
         'field_migrator': return_list
         },
        {'AT_field_name': 'subject',
         'DX_field_name': 'subject',
         },
    )
    migrateCustomAT(
        fields_mapping,
        src_type='PoiIssue',
        dst_type='Issue')
    # All issues now appear to be in the 'new' state.
    # The workflow *has* been migrated, but it is not yet in the catalog.
    # So update the catalog info.
    # Same problem may be there for trackers, when you have custom workflow,
    # so handle those too.
    logger.info('Updating security info.')
    catalog = getToolByName(context, 'portal_catalog')
    # Note: we need the *new* dexterity type names.
    for brain in catalog.unrestrictedSearchResults(
            portal_type=['Issue', 'Tracker']):
        path = brain.getPath()
        try:
            obj = brain.getObject()
        except (AttributeError, ValueError, TypeError):
            logger.warn('Error getting object from catalog for path %s', path)
            continue
        # We need to reindex the review_state.
        # And the object security (allowedRolesAndUsers) seems good too.
        obj.reindexObject(idxs=['review_state'])
        obj.reindexObjectSecurity()
