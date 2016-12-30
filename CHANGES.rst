Changelog for Poi
=================


2.3 (2016-12-30)
----------------

- Avoid security warning on startup.  You get a warning about our
  IResponseAdder viewlet manager, which apparently has a security
  declaration for nonexistent method '__getitem__'.  So we add that
  method and let it return an IndexError, because this is a
  ``zope.contentprovider`` which is not meant to iterate over
  viewlets.  [maurits]

- Use blob file for attachments in issues and responses.  This comes
  with an upgrade step to migrate them.
  Fixes `issue #32 <https://github.com/collective/Products.Poi/issues/32>`_.
  [maurits]


2.2.10 (2016-12-23)
-------------------

- Added basic options to ``BasePoiMail``.  This avoids doing the same
  calculations on various sub classes.  [maurits]

- Load ``rss.png`` instead of ``rss.gif``.  [maurits]

- Fixed ``poi.js`` javascript for newer jQuery versions.  1.9 would
  fall over an undefined ``jQuery.browser``.  1.7 would fall over an
  unrecognized expression, needing extra quotes.  Still works on 1.4.
  Fixes `issue 30 <https://github.com/collective/Products.Poi/issues/30>`_.
  [maurits]


2.2.9 (2016-12-09)
------------------

- Only do link detection in plain or intelligent text fields.  If a
  field has html and contains an html space ``&#160`` and you have an
  issue 160, it will start looking very ugly.  Note that by default
  html is not allowed.  [maurits]


2.2.8 (2015-08-31)
------------------

- Require Products.DataGridField 1.9.2 as minimum.  This means we no
  longer use the ``isDataGridFilled`` validator, but simply rely on
  ``required=True`` for the ``availableAreas`` and
  ``availableIssueTypes`` fields of the trackers.
  [maurits]


2.2.7 (2014-09-10)
------------------

- Refer to .png Plone images in css instead of .gif.
  [thomasdesvenain]

- When we go to search form, current filters are pre-selected.
  [thomasdesvenain]

- Filled in missing translations for de and removed stale fuzzy entries
  [pilz]


2.2.6 (2013-10-18)
------------------

- Show technicians in the responsible managers list in the search
  form.
  Fixes http://plone.org/products/poi/issues/266
  [maurits]

- Sort the available releases of trackers in PloneSoftwareCenter by
  id, which means: by version.
  [maurits]

- Fix auto-recognized issue/revision links when displayed in the
  tracker log.  These would point outside of the tracker.  Now we pass
  the absolute url of the tracker.  Note that responses cache their
  rendered html text in a variable ``rendered_text``, which is only
  updated when you edit the response, so this may not have effect on
  existing responses.
  Fixes http://plone.org/products/poi/issues/255
  [maurits]

- Fix corner cases in recognizing links to issues and revisions.  Add
  the patterns for these two in ``config.py`` so they can be
  overridden.  Also add the template to use when recognizing a link to
  another issue there.
  Fixes http://plone.org/products/poi/issues/262
  [maurits]


2.2.5 (2013-08-22)
------------------

- Fixed mail templates styles for new issue and new response
  [cekk]

- Some style fixes; removed all inline styles left, translated to
  CSS rules.
  [keul]

2.2.4 (2013-07-02)
------------------

- Removed the text type selection for the tracker description.  Note:
  when editing and saving an existing tracker and it has html code in
  its description, you may get a validation error: "Mimetype text/html
  is not allowed."  In that case you need to edit the description and
  remove the html tags.
  [keul]

- Some style fixes; removed inline styles.
  [keul]


2.2.3 (2013-04-18)
------------------

- Also allow text/plain for the details field.  This fixes a problem
  with Plone 4.3.
  [maurits]

- Updated italian translation
  [keul]

- Now supporting the "Site Administrator" role
  [keul]

- Fix tracker security; issues inside private folder
  must not be visible to anonymous users
  [keul]


2.2.2 (2013-04-04)
------------------

- Show the 'Watch/Stop watching this tracker' button again.
  [maurits]

- Fixed ``KeyError: portal`` on several pages for anonymous users.
  [maurits]


2.2.1 (2013-03-30)
------------------

- Issue search form criteria can be pre-selected from request.
  [thomasdesvenain]

- Quick search and add issue button are now available on all pages.
  [thomasdesvenain]

- Most metadata are now clickable links.
  [thomasdesvenain]

- Added issue_portal_type parameter in IssueFolderView.  It is now
  possible to use a custom content type inherited from PoiIssue.
  [cedricmessiant]


2.2 (2013-02-07)
----------------


- Completed French translations.
  [cedricmessiant]

- Store the watchers of a tracker in a lines field instead of
  annotations.  This way, you can edit them as Manager if that is
  needed.  Added an upgrade step to migrate all existing trackers.
  [maurits]

- Fixed changes in a response that were being saved with a wrong id.
  This did not cause missing data, just a duplicate id in the response
  changes.  This is never shown in the UI, so should only be a problem
  for third party code that directly accesses this response data
  structure.
  https://github.com/collective/Products.Poi/issues/4
  [maurits]


2.1.4 (2012-12-03)
------------------

- Fix advanced search form not returning results unless both `Issue
  number` and `Submitter` were specified.
  [rpatterson]


2.1.3 (2012-11-28)
------------------

- Fixed reinstall error.  Metadata would be missing in the catalog
  brains.
  [maurits]

- Included Products.AddRemoveWidget and Products.DataGridField in configure.zcml
  [cedricmessiant]


2.1.2 (2012-11-06)
------------------

- Fixed packaging error.
  [maurits]


2.1.1 (2012-11-06)
------------------

- Made compatible with Plone 4.3.  Lost compatibility with Plone 4.0.
  [maurits]

- Fix Unauthorized/"Insufficient Privileges" error under Plone 4.2.
  [rpatterson]


2.1.0 (2012-06-28)
------------------

- completed german translation [jensens]


2.1.0b1 (2012-05-02)
--------------------

- Get rid of all code that still handled old PoiResponses.  If you
  still have those (meaning you were using Poi 1.1.x before this),
  then you must first update to version 2.0.x and run the upgrade
  steps.
  [maurits]

- Add an uninstall method and profile, to clean up a bit more.  In
  addition to what the CMFQuickInstaller does, we remove our catalog
  columns and indexes, our skin layer from the skin selections, and
  our types from the parentMetaTypesNotToQuery in the
  navtree_properties.
  [maurits]

- Refactored all email notifications to templates. This should make it
  easier to customize and translate.
  [maurits]

- Fixed example link for collective changesets.
  [maurits]

- When clicking on the suggested login button, show a popup.
  [maurits]

- Removed htmlrender.py.
  [maurits]

- Refactored the email notifications by creating a page template
  ``browser/poi_mail.pt`` and a css file ``skins/Poi/poi-email.css``
  and using that instead of hardcoded stuff in a python file
  ``htmlrender.py``.
  Fixes http://plone.org/products/poi/issues/251
  [maurits]

- Allow assigning portlets to trackers and issues.
  Fixes http://plone.org/products/poi/issues/250
  [maurits]

- Make sure the issue-info-box does not inherit a 100% width, as is the
  case on plone.org at the moment (6 September 2011), which is far too
  wide for this little box.
  See http://plone.org/products/poi/issues/249
  [Maurits]

- Added MANIFEST.in file so that .mo translation files will be
  included in source distributions (with help from zest.releaser and
  zest.pocompile).
  Refs http://plone.org/products/poi/issues/248
  [maurits]


2.0.2 (2011-04-09)
------------------

- Depend on Products.CMFPlone instead of Plone to improve Plone 4.1
  compatibility.
  [maurits]

- Do not fail when rendering a response that has a text/x-html-safe
  mimetype or where the html transform returns nothing.  (Merged from
  1.2 branch.)
  [maurits]

- Review French translations
  [toutpt]


2.0.1 (2010-11-11)
------------------

- Split profile registration and upgrade steps from configure.zcml
  into a new profiles.zcml as it is quite big already.
  [maurits]

- Fix: for the 'no change' label and input the ids were empty.
  [thomasdesvenain]

- Removed our dependency on collective.autopermission, as its
  functionality is integrated in Zope 2.12 (Plone 4.0).
  [maurits]


2.0 (2010-10-14)
----------------

- Lower the minimum dependency on Products.AddRemoveWidget to 1.4.2
  again, as I had a report about a performance hit in 1.4.3 in corner
  cases not related to Poi itself; and 1.4.2 is fine really, though
  1.4.4 has a fix for Plone 4 in a part that Poi does not use.
  [maurits]

- Do not advise users to click on 'search for issues' as that link is
  nowhere; instead it should be 'Advanced issue search'.
  [maurits]

For changes in 2.0b2 and earlier, see ``docs/HISTORY.txt``.
