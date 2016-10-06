Poi: A friendly issue tracker
=============================

 by Martin Aspeli <optilude@gmx.net>

 current maintainer: Maurits van Rees <maurits@vanrees.org>

 Released under the GNU General Public License, version 2
 
Poi is an issue tracker product for Plone. It has a goal to be 
simple and attractive whilst providing the most commonly needed issue
tracking functionality. Poi 3.0 uses Dexterity and is for Plone 5.

Feedback is very welcome. 

Please submit any bugs or feature requests at: 
    
    https://github.com/collective/Products.Poi/issues


Installation and dependencies
-----------------------------

Best is to use zc.buildout.  Just add Products.Poi to your eggs, rerun
buildout and you are done.  Optionally add
Products.PloneSoftwareCenter.

Poi 3.0+ requires:

  - Plone 5
  - collective.watcherlist


Upgrading
---------

Re-install Poi from the Add/Remove Products control panel.  Some
upgrade steps will be executed; these can also be found in the ZMI, in
portal_setup, on the Upgrade tab, in case you need to run them again.
Backup your Data.fs first before upgrading!


Usage
-----

Add a Tracker, and use the "state" menu to open it for submissions. 
Available workflow states are:

 * `Open`: Anonymous users can view and submit issues
 * `Restricted`: Anonymous users can view, but only members can submit
 * `Protected`: Only members can view and submit
 * `Closed`: Tracker is closed to submissions
 
The tracker front pages allows you to browse for issues by release,
state or area, as well as search for issues. Note that if you are not
tracking software releases, you can leave the list of "releases"
empty, and organization by release will be turned off. The fields for
areas and issue types come pre-configured with simple values that
presume you are tracking software bugs.  You can change these to
whatever you want.

Once you have set up the tracker, add Issues inside, and Responses
inside Issues. Anyone can add responses to issues with the default
workflow. Responses from tracker managers (as configured on the root
tracker object) and the original submitter are color coded to make
them easier to pick out. When adding a response as a tracker manager,
you can change the state, importance or assignment of an issue.

If email notification is enabled in the root tracker object, managers
will get an email when there are new issues and responses, optionally
via a mailing list. Issue submitters will also get emails upon issue
responses. Additionally, when an issue is marked as "resolved" by a
tracker manager, the submitter will receive an email asking him or her
to mark the issue as confirmed closed.

For a look at how the various workflow states of an issue are
connected, take a look at the attachment added by `bethor` to this
issue: http://old.plone.org/products/poi/issues/179


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
