Poi: A friendly issue tracker
=============================

by Martin Aspeli <optilude@gmx.net>

current maintainer: Maurits van Rees <maurits@vanrees.org>

Released under the GNU General Public License, version 2

Poi is an issue tracker product for Plone. It has a goal to be 
simple and attractive whilst providing the most commonly needed issue
tracking functionality. Poi 3.0 uses Dexterity and is for Plone 5 only.

Feedback is very welcome. 

Please submit any bugs or feature requests at: 
   
   https://github.com/collective/Products.Poi/issues


Installation and dependencies
-----------------------------

This version of Poi is for migrating between 2.x and 3.x. If you are
installing Poi for the first time, see the next section for which
version to use.


What version of Poi to use?
---------------------------

* Poi 2.0 - 2.4 is for Plone 4
* Poi 2.5 is a migration step from Poi 2.x to Poi 3.x
* Poi 3.0+ only works on Plone 5


Upgrading
---------

Version 2.5.x of Poi is only for migrating to Dexterity in preparation of
moving to Plone 5. It requires plone.app.contenttypes*, but don't activate
the add-on unless you plan on migrating all your default Archetypes
to Dexterity.

`*` Requires plone.app.contenttypes after 1.1.1, if released. If a new
version in the 1.1.x series is not available, you can use 1.1.1.1
from http://dist.sixfeetup.com/public

Upgrade steps:

* Do the Poi migration in Plone 4 (reinstall Poi or run the upgrade steps)
* Upgrade to Plone 5
* Upgrade to Poi 3.0

Re-install Poi from the Add/Remove Products control panel.  Some
upgrade steps will be executed; these can also be found in the ZMI, in
portal_setup, on the Upgrade tab, in case you need to run them again.
Backup your Data.fs first before upgrading!


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

 o Plone 5 Refactoring by Six Feet Up
