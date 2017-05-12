Poi: A friendly issue tracker
=============================

by Martin Aspeli <optilude@gmx.net>

current maintainer: Maurits van Rees <maurits@vanrees.org>

Released under the GNU General Public License, version 2

Poi is an issue tracker product for Plone. It has a goal to be 
simple and attractive whilst providing the most commonly needed issue
tracking functionality. Poi 4.0 uses Dexterity and is for Plone 5 only.

Feedback is very welcome. Please submit any bugs or feature requests at:
   
   https://github.com/collective/Products.Poi/issues


Installation and dependencies
-----------------------------

This version of Poi is for migrating between 2.x and 4.x. If you are
installing Poi for the first time, see the next section for which
version to use.


What version of Poi to use?
---------------------------

* Poi 2.x is for Plone 4
* Poi 3.x is a migration step from Poi 2.x to Poi 4.x
* Poi 4.0+ only works on Plone 5


Upgrading
---------

Version 3.x of Poi is only for migrating to Dexterity in preparation of
moving to Plone 5. It requires plone.app.contenttypes 1.1.2, but don't activate
the add-on unless you plan on migrating all your default Archetypes
to Dexterity.

Upgrade steps:

* Do the Poi migration in Plone 4 (reinstall Poi or run the upgrade steps)
* Upgrade to Plone 5
* Upgrade to Poi 4.x

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
