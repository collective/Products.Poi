#!/bin/bash
# Run this script to update the translations.

# Do you want to add translations for a new language?  Great!
# You need to know your language code.  Say it is xx.  Then do this:
# - Copy poi.pot to poi-xx.po
# - Copy plone-poi.pot to plone-poi-xx.po
# - Change the headers in those new files to fit your language.
# - Add your translations in those files.
# - Commit the new files to the Plone collective, or:
# - Add them to the Poi issue tracker on plone.org:
#   http://plone.org/products/poi/issues
# - Problems?  Ask for help on the internationalization forum:
#   http://www.nabble.com/Internationalization-f6748.html

i18ndude rebuild-pot --pot poi.pot --create Poi --merge poi-manual.pot --exclude="poi-my-issues-rss.xml.pt poi-orphaned-issues-rss.xml.pt poi-issue-search-rss.xml.pt" ../

i18ndude sync --pot plone-poi.pot `find . -iregex '.*plone-.*\.po$'`

i18ndude  sync --pot poi.pot  `find . -iregex '.*\.po$'|grep -v plone`
