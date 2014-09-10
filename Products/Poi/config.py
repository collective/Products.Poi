# -*- coding: utf-8 -*-

PROJECTNAME = "Poi"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
ADD_CONTENT_PERMISSIONS = {
    'PoiTracker': 'Poi: Add Tracker',
    'PoiIssue': 'Poi: Add Issue',
}

product_globals = globals()

DESCRIPTION_LENGTH = 200
PSC_TRACKER_ID = 'issues'

# Add text/html to the list of mimetypes to allow HTML/kupu
# issue/response text.
ISSUE_MIME_TYPES = ('text/x-web-intelligent', 'text/plain')
DEFAULT_ISSUE_MIME_TYPE = 'text/x-web-intelligent'
# Patterns used for recognizing links to issues and revisions:
ISSUE_RECOGNITION_PATTERNS = \
    [r'\B#[1-9][0-9]*\b', r'\bissue:[1-9][0-9]*\b',
     r'\bticket:[1-9][0-9]*\b', r'\bbug:[1-9][0-9]*\b']
REVISION_RECOGNITION_PATTERNS = \
    [r'\br[0-9]+\b', r'\bchangeset:[0-9]+\b', r'\B\[[0-9]+\]\B']
# Template to use when recognizing a link to another issue:
ISSUE_LINK_TEMPLATE = '<a href="%(base_url)s/%(bug)s">%(linktext)s</a>'
