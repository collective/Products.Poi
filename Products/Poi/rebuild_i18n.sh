#!/bin/bash
# Run this script to update the translations.

# Do you want to add translations for a new language?  Great!
# You need to know your language code.  Say it is xx.  Then do this:
# - Create directories locales/xx and locales/xx/LC_MESSAGES
# - Copy locales/Poi.pot to locales/xx/LC_MESSAGES/Poi.po
#   (note the capital letter in Poi.po)
# - Copy locales/plone.pot to locales/xx/LC_MESSAGES/plone.po
# - Change the headers in those new files to fit your language.
# - Add your translations in those files.
# - Commit the new files to the Plone collective, or:
# - Add them to the Poi issue tracker on plone.org:
#   http://plone.org/products/poi/issues
# - Problems?  Ask for help on the internationalization forum:
#   http://www.nabble.com/Internationalization-f6748.html

i18ndude rebuild-pot --pot locales/poi.pot --create Poi --exclude="poi-my-issues-rss.xml.pt poi-orphaned-issues-rss.xml.pt poi-issue-search-rss.xml.pt" .

# Sync plone po files; but commented out by default as we have no code that updates the plone.pot file.
# i18ndude sync --pot locales/plone.pot $(find . -name 'plone-.po')

i18ndude sync --pot locales/Poi.pot $(find . -name 'Poi.po')
