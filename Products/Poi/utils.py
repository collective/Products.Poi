import re


# Patterns used for recognizing links to issues and revisions:
ISSUE_RECOGNITION_PATTERNS = (
    r'\B#[1-9][0-9]*\b',
    r'\bissue:[1-9][0-9]*\b',
    r'\bticket:[1-9][0-9]*\b',
    r'\bbug:[1-9][0-9]*\b',
)
REVISION_RECOGNITION_PATTERNS = (
    r'\br[0-9]+\b',
    r'\bchangeset:[0-9]+\b',
    r'\B\[[0-9]+\]\B',
)
# Template to use when recognizing a link to another issue:
ISSUE_LINK_TEMPLATE = '<a href="%(base_url)s/%(bug)s">%(linktext)s</a>'


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
            rev = getNumberFromString(linktext)

            pos = res.start() + 1
            link = '<a href="' + repo_url % {'rev': rev} + '">' + linktext + \
                '</a>'
            text = text[0: pos - 1] + link + text[res.end():]
            pos += len(link)

    return text


def is_email(value):
    expr = re.compile(
        r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$",
        re.IGNORECASE
    )
    return bool(expr.match(value))
