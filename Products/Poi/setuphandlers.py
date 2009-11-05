from Products.CMFCore.utils import getToolByName


def add_catalog_indexes(site, logger):
    """Add our indexes to the catalog.

    Doing it here instead of in profiles/default/catalog.xml means we
    do not need to reindex those indexes after every reinstall.
    """
    catalog = getToolByName(site, 'portal_catalog')
    indexes = catalog.indexes()
    wanted = ("getRelease", "getArea", "getIssueType", "getSeverity",
              "getTargetRelease", "getResponsibleManager")

    missing = [w for w in wanted if w not in indexes]
    if missing:
        for name in missing:
            catalog.addIndex(name, 'FieldIndex')
            logger.info("Added FieldIndex for field %s.", name)
        logger.info("Indexing new indexes %s.", ', '.join(missing))
        catalog.manage_reindexIndex(ids=missing)


def allow_psc_tracker(site, logger):
    """Add PoiPscTracker to allowed types in PSCProject.

    Fails gracefully if PSCProject does not exist.
    """
    types_tool = getToolByName(site, 'portal_types')
    fti = getattr(types_tool, 'PSCProject', None)
    if fti is None:
        logger.info("Could not add PoiPscTracker to allowed content types of "
                    "PSCProject as it does not exist.")
        return
    allowed_types = list(fti.allowed_content_types)
    if 'PoiPscTracker' in allowed_types:
        logger.info("PoiPscTracker is already in allowed content types of "
                    "PSCProject.")
    allowed_types.append('PoiPscTracker')
    fti.allowed_content_types = tuple(allowed_types)
    logger.info("Added PoiPscTracker to allowed content types PSCProject.")


def import_various(context):
    # Only run step if a flag file is present
    if context.readDataFile('poi_various.txt') is None:
        return
    logger = context.getLogger('Poi')
    site = context.getSite()
    add_catalog_indexes(site, logger)
    allow_psc_tracker(site, logger)
