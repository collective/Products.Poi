#!/bin/bash

i18ndude rebuild-pot --pot poi.pot --create Poi --merge poi-manual.pot --exclude="poi-my-issues-rss.xml.pt poi-orphaned-issues-rss.xml.pt poi-issue-search-rss.xml.pt" ../

i18ndude sync --pot plone-poi.pot `find . -iregex '.*plone-.*\.po$'`

i18ndude  sync --pot poi.pot  `find . -iregex '.*\.po$'|grep -v plone`
