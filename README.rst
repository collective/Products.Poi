Poi: A friendly issue tracker
=============================

 by Martin Aspeli <optilude@gmx.net>

 current maintainer: Maurits van Rees <maurits@vanrees.org>

 Released under the GNU General Public License, version 2
 
Poi is an issue tracker product for Plone. It has three overarching aims:

- Provide the default tracker for open source software projects on
  http://plone.org

- Be simple and attractive whilst providing the most commonly needed issue
  tracking functionality.

- Optionally integrate with the PloneSoftwareCenter to allow
  individual products to have their own issue trackers

Poi is not and will not be a track-anything-and-everything tracker, a help desk
product or anything else. If Poi is too simple for your needs, you may want to
look at something like PloneCollectorNG.

Feedback is very welcome. 

Please submit any bugs or feature requests at: 
    
    http://plone.org/products/poi/issues
    
(Yes, this is a Poi tracker). Please do search the tracker first, so we can
avoid unnecessary duplicates.
    
See http://plone.org/products/poi for the latest release and the development 
road map.


Installation and dependencies
-----------------------------

Best is to use zc.buildout.  Just add Products.Poi to your eggs, rerun
buildout and you are done.  Optionally add
Products.PloneSoftwareCenter.

Poi requires:

  - Plone 4; this version of Poi will *not* work with Plone 3.

  - DataGridField

  - AddRemoveWidget

  - collective.watcherlist

  - For PloneSoftwareCenter integration, PloneSoftwareCenter is
    required.  See http://plone.org/products/plonesoftwarecenter
    Tested with PloneSoftwareCenter 1.5.

For new installations, install using Add/Remove Products as normal. If you want
PloneSoftwareCenter configuration to be automatically configured, install PSC
*first*.


Upgrading
---------

Re-install Poi from the Add/Remove Products control panel.  Some
upgrade steps will be executed; these can also be found in the ZMI, in
portal_setup, on the Upgrade tab, in case you need to run them again.
Backup your Data.fs first before upgrading!


Usage
-----

Add a Tracker, and use the "state" menu to open it for submissions. 
 
The tracker front pages allows you to browse for issues by release,
state or area, as well as search for issues. Note that if you are not
tracking software releases, you can leave the list of "releases"
empty, and organisation by release will be turned off. The fields for
areas and issue types come pre-configured with simple values that
presume you are tracking software bugs.  You can change these to
whatever you want.

Once you have set up the tracker, add Issues inside, and Responses
inside Issues. Anyone can add responses to issues with the default
workflow. Responses from tracker managers (as configured on the root
tracker object) and the original submitter are colour coded to make
them easier to pick out. When adding a response as a tracker manager,
you can change the state, importance or assignment of an issue.

If email notification is enabled in the root tracker object, managers
will get an email when there are new issues and responses, optionally
via a mailing list. Issue submitters will also get emails upon issue
responses. Additionally, when an issue is marked as "resolved" by a
tracker manager, the submitter will receive an email asking him or her
to mark the issue as confirmed closed.

To use with the PloneSoftwareCenter, install PSC and *then* install
Poi. This will ensure PoiPscTracker is added to the list of allowed
content types in portal_types/PSCProject. You can then add Trackers
inside a project in the software center. The trackers will function in
the same way as regular trackers, but will use releases from the
software center project instead of a manually defined list.

For a look at how the various workflow states of an issue are
connected, take a look at the attachment added by bethor to this
issue: http://plone.org/products/poi/issues/179


Using HTML/kupu and other markups for issue text:
-------------------------------------------------

 **Please see notes about migration above!**

Before version 1.0b2 Poi used to support kupu/rich text fields with HTML in the
issue and response body. This was removed in favour of "intelligenttext", a
plain-text markup that preserves whitespace and makes links clickable.

This was found to work very well on plone.org and for the type of simple 
trackers that Poi was intended for. However, a lot of users wanted kupu back.

To get kupu back, you will need to edit Poi/config.py::

  ISSUE_MIME_TYPES = ('text/x-web-intelligent', 'text/html')
  DEFAULT_ISSUE_MIME_TYPE = 'text/html'

You may also need to re-install Poi, and perform an Archetypes schema update,
by going to archetypes_tool, and the Schema Update tab in the ZMI.

And you may need to remove some conditional expressions in the
portal_javascripts to make sure all needed scripts load (at least for
TinyMCE).

Please note one **very important** thing:

- If you upgrade Poi, you are likely to have to make this change again!


Credits
-------

If you have contributed to Poi in some fashion, be sure to add
yourself in the hall of fame here!

 o Design and development by Martin Aspeli <optilude@gmx.net>

 o Bug fixes and general critiquing by Rocky Burt <rocky@serverzen.com>

 o Icons by Vidar Andersen, Black Tar, originally created for CMFCollector.

 o Log-view for Poi trackers by Malthe Borch

 o Link detection, additions to the search interface and other fixes
   by Daniel Nouri.

 o Plone 3 support by Alexander Limi and Maurits van Rees.

 o Bug fixes, modernizing of responses, maintenance by Maurits van
   Rees

 o Plone 4 support by Maurits van Rees and Maarten Kling.

 o Refactoring of emailing and watching code into
   collective.watcherlist: Maurits van Rees.
