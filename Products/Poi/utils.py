from Products.CMFPlone.utils import safe_unicode
from Products.Poi.config import ISSUE_LINK_TEMPLATE

import re


try:
    from plone.i18n.normalizer.interfaces import \
        IUserPreferredFileNameNormalizer
    FILE_NORMALIZER = True
except ImportError:
    FILE_NORMALIZER = False


def getNumberFromString(linktext):
    """
    Extract the number from a string with a number in it.
    From 'foo666bar' we get '666'.
    (From 'foobar' we probably end up with problems.)
    """
    pattern = re.compile('[1-9][0-9]*')
    res = pattern.search(linktext)
    if res is not None:
        return linktext[res.start(): res.end()]


def linkBugs(text, ids, patterns, base_url='..'):
    """
    Replace patterns with links to other issues in the same tracker.
    """
    for raw in patterns:
        pos = 0
        pattern = re.compile(raw)
        while True:
            res = pattern.search(text, pos)
            if res is None:
                break
            pos = res.start()

            linktext = text[res.start(): res.end()]
            bug = getNumberFromString(linktext)

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


def linkSvn(text, svnUrl, patterns):
    """
    Replace patterns with links to changesets in a repository.
    (What says it has to be svn?)
    """

    if len(svnUrl) == 0:
        return text

    for raw in patterns:
        pos = 0
        pattern = re.compile(raw)
        while True:
            res = pattern.search(text, pos)
            if res is None:
                break

            linktext = text[res.start(): res.end()]
            rev = getNumberFromString(linktext)

            pos = res.start() + 1
            link = '<a href="' + svnUrl % {'rev': rev} + '">' + linktext + \
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
