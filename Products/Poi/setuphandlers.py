import logging
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.upgrade import _upgrade_registry
from Products.GenericSetup.registry import _profile_registry


def add_catalog_indexes(site, logger):
    """Add our indexes to the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.
    """
    catalog = getToolByName(site, 'portal_catalog')
    indexes = catalog.indexes()
    wanted = ("release", "area", "issue_type", "severity",
              "target_release", "assignee")

    missing = [w for w in wanted if w not in indexes]
    if missing:
        for name in missing:
            catalog.addIndex(name, 'FieldIndex')
            logger.info("Added FieldIndex for field %s.", name)
        logger.info("Indexing new indexes %s.", ', '.join(missing))
        catalog.manage_reindexIndex(ids=missing)


def runUpgradeSteps(profile_id):
    """run the upgrade steps for the given profile_id in the form of:

    profile-<package_name>:<profile_name>

    example:

    profile-my.package:default

    Basically this is the code from GS.tool.manage_doUpgrades() in step
    form.  Had to extract the code because it was doing a redirect back to the
    upgrades form in the GS tool.
    """
    portal = api.portal.get()
    setup_tool = getToolByName(portal, 'portal_setup')
    logger = logging.getLogger(__name__)
    logger.info('****** runUpgradeSteps BEGIN ******')
    upgrade_steps = setup_tool.listUpgrades(profile_id)
    steps_to_run = []
    for step in upgrade_steps:
        if isinstance(step, list):
            # this is a group of steps
            for new_step in step:
                steps_to_run.append(new_step['step'].id)
        else:
            steps_to_run.append(step['step'].id)

    #################
    # from GS tool...
    ##################
    for step_id in steps_to_run:
        step = _upgrade_registry.getUpgradeStep(profile_id, step_id)
        if step is not None:
            step.doStep(setup_tool)
            msg = "Ran upgrade step %s for profile %s" % (step.title,
                                                          profile_id)
            logger.info(msg)

    # XXX should be a bit smarter about deciding when to up the
    #     profile version
    profile_info = _profile_registry.getProfileInfo(profile_id)
    version = profile_info.get('version', None)
    if version is not None:
        setup_tool.setLastVersionForProfile(profile_id, version)

    logger.info('****** runUpgradeSteps END ******')


def import_various(context):
    # Only run step if a flag file is present
    if context.readDataFile('poi_various.txt') is None:
        return
    logger = context.getLogger('Poi')
    site = context.getSite()
    add_catalog_indexes(site, logger)
    runUpgradeSteps('profile-Products.Poi:default')
