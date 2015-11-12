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


def import_various(context):
    # Only run step if a flag file is present
    if context.readDataFile('poi_various.txt') is None:
        return
    logger = context.getLogger('Poi')
    site = context.getSite()
    add_catalog_indexes(site, logger)
