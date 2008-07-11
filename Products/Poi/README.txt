Poi: A friendly issue tracker
=============================

 by Martin Aspeli <optilude@gmx.net>
 current maintainer: Maurits van Rees <maurits@vanrees.org>
 Released under the GNU General Public License, version 2
 
Poi is an issue tracker product for Plone. It has three overarching aims:

- Work with, not against Plone.

- Be simple and attractive whilst providing the most commonly needed issue
  tracking functionality.

- Optionally integrate with the PloneSoftwareCenter to allow
  individual products to have their own issue trackers

Poi is not and will not be a track-anything-and-everything tracker, a help desk
product or anything else. If Poi is too simple for your needs, you may want to
look at something like PloneCollectorNG.

Feedback is very welcome. 

Please submit any bugs or feature requests to at: 
    
    http://plone.org/products/poi/issues
    
(Yes, this is a Poi tracker). Please do search the tracker first, so we can
avoid unnecessary duplicates.
    
See http://plone.org/products/poi for the latest release and the development 
roadmap.


Using HTML/kupu and other markups for issue text:
-------------------------------------------------

 **Please see notes about migration below!**

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

Please note one **very important** thing:

- If you upgrade Poi, you're likely to have to make this change again!


Installation and dependencies
-----------------------------

Poi requires:

  - Plone: 3.0+ on Zope 2.10
  - DataGridField (*)
  - AddRemoveWidget

  - intelligenttext (but this is installed by default in Plone 3)
    Note: when going from Plone 2.5 to 3.0, please first uninstall
    intelligenttext, then create a new instance with Plone 3.  Then
    run the portal_migration, which will install the new
    plone.intelligenttext library for you.
  
  - For PloneSoftwareCenter integration, PloneSoftwareCenter is
    required.  See http://plone.org/products/plonesoftwarecenter
    Tested on Plone 2.5 with: PloneSoftwareCenter-1.0-RC.tgz
    Tested on Plone 3.0 with: PloneSoftwareCenter-1.5-alpha1.tar.gz

(*) NOTE: Before version 1.0 beta 2, ArchAddOn was required instead of
DataGridField.  Also note that PloneSoftwareCenter does required
ArchAddOn.

For new installations, install using Add/Remove Products as normal. If you want
PloneSoftwareCenter configuration to be automatically configured, install PSC
*first*. 


Upgrading
---------

Re-install Poi from the Add/Remove Products control panel or
portal_quickinstaller in the ZMI.

Poi 1.2 gets rid of old Archetypes based PoiResponses and introduces
new light weight zope-3-style responses; this needs a migration.  In
the ZMI go to portal_setup, then the Upgrades tab and run any upgrade
steps that are available for Poi.  Backup your Data.fs first!

After any upgrade, run an Archetypes schema update, by going to
'archetype_tool' in the ZMI, selecting the 'Update Schema' tab,
selecting all the 'Poi.*' types, and clicking 'Update schema'. It's
probably a good idea to choose 'All objects' from the drop-down as
well, although this will take slightly longer.

If you get errors about things being 'Missing', try to update your catalog,
by going to portal_catalog in the ZMI, clicking the Advanced tab, and then
the 'Update catalog' button.


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
via a mailing list. Issue submittes will also get emails upon issue
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
