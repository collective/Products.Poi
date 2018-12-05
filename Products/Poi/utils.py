from Products.CMFPlone.utils import safe_unicode

import re

try:
    from plone.i18n.normalizer.interfaces import \
        IUserPreferredFileNameNormalizer
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False

# Patterns used for recognizing links to issues and revisions:
ISSUE_RECOGNITION_PATTERNS = (
    r'\B#([1-9][0-9]*)\b',
    r'\bissue:([1-9][0-9]*)\b',
    r'\bticket:([1-9][0-9]*)\b',
    r'\bbug:([1-9][0-9]*)\b',
)
REVISION_RECOGNITION_PATTERNS = (
    r'\br([0-9]+)\b',
    r'\br([0-9a-f]{5,})\b',
    r'\bchangeset:([0-9a-f]+)\b',
    r'\B\[([0-9a-f]+)\]\B',
)
# Template to use when recognizing a link to another issue:
ISSUE_LINK_TEMPLATE = '<a href="%(base_url)s/%(bug)s">%(linktext)s</a>'


def link_bugs(text, ids, base_url='..'):
    """
    Replace patterns with links to other issues in the same tracker.
    """
    for raw in ISSUE_RECOGNITION_PATTERNS:
        pos = 0
        pattern = re.compile(raw)
        while True:
            res = pattern.search(text, pos)
            if res is None:
                break
            pos = res.start()

            linktext = text[res.start(): res.end()]
            bug = res.group(1)

            if bug is not None and bug in ids:
                link = ISSUE_LINK_TEMPLATE % dict(
                    base_url=base_url,
                    bug=bug,
                    linktext=linktext)
                text = text[0:pos] + link + text[res.end():]
                pos += len(link)
            else:
                pos += 1

    return text


def link_repo(text, repo_url):
    """
    Replace patterns with links to changesets in a repository.
    """

    if len(repo_url) == 0:
        return text

    for raw in REVISION_RECOGNITION_PATTERNS:
        pos = 0
        pattern = re.compile(raw)
        while True:
            res = pattern.search(text, pos)
            if res is None:
                break

            linktext = text[res.start(): res.end()]
            rev = res.group(1)

            pos = res.start() + 1
            link = '<a href="' + repo_url % {'rev': rev} + '">' + linktext + \
                '</a>'
            text = text[0: pos - 1] + link + text[res.end():]
            pos += len(link)

    return text


def normalize_filename(filename, request):
    if FILE_NORMALIZER:
        # Get something the user can recognise.
        filename = IUserPreferredFileNameNormalizer(request).normalize(
            filename)
    filename = safe_unicode(filename)
    # Also, get something that does not raise a ConstraintNotSatisfiedError
    # when migrating to blob attachments.  Found in live data: a filename that
    # includes a newline...
    filename = filename.replace('\n', ' ').replace('\r', ' ')
    return filename


def is_email(value):
    expr = re.compile(
        r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$",
        re.IGNORECASE
    )
    return bool(expr.match(value))
