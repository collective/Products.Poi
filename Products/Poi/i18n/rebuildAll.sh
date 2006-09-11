#!/bin/bash

i18ndude rebuild-pot --pot poi.pot --create poi --merge poi-manual.pot `find ../skins/ -iregex '.*\..?pt$'`

i18ndude sync --pot plone-poi.pot `find . -iregex '.*plone-.*\.po$'`

i18ndude  sync --pot poi.pot  `find . -iregex '.*\.po$'|grep -v plone`