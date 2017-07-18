Poi: A friendly issue tracker
=============================

Poi is an issue tracker product for Plone. It has a goal to be 
simple and attractive whilst providing the most commonly needed issue
tracking functionality. Poi 4.0 uses Dexterity and is for Plone 5 only.

 by Martin Aspeli <optilude@gmx.net>

 current maintainer: Maurits van Rees <maurits@vanrees.org>

 Released under the GNU General Public License, version 2

.. image:: https://img.shields.io/travis/collective/Products.Poi/master.svg
    :target: http://travis-ci.org/collective/Products.Poi


Feedback is very welcome. Please submit any bugs or feature requests at: 
    
    https://github.com/collective/Products.Poi/issues


Installation and dependencies
-----------------------------

Best is to use zc.buildout.  Just add Products.Poi to your eggs, rerun
buildout and you are done.  

Poi 4.0+ requires:

  - Plone 5
  - collective.watcherlist


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

* Do the migration in Plone 4 (reinstall Poi or run the upgrade steps)
* Upgrade to Plone 5
* Upgrade to Poi 4.x

Re-install Poi from the Add/Remove Products control panel.  Some
upgrade steps will be executed; these can also be found in the ZMI, in
portal_setup, on the Upgrade tab, in case you need to run them again.
Backup your Data.fs first before upgrading!


Usage
=====

Poi is a folderish object type. Many Poi Trackers can exist within the
same Plone instance.

Prior to adding a new Tracker, ensure that some Assignees (users) are
created in the system.


Tracker Usage
-------------

Add a new Tracker, and customize the following to suit your
organization's needs:

- Areas - top level categories for the Tracker (e.g., UI)
- Issue Types -- ticket types in the system (e.g., Bug)
- Severities - levels of severity for the Issues (e.g., Low)
- Available Releases -- used for assigning version values (e.g. v1.0)
- Assignees -- list of users to whom Issues can be assigned
- Watchers -- list of users who should be notified when Issues or comments are added
- Mailing List -- single email address, similar to Watchers
- Repository URL -- git/subversion repository used by your organization 

Note that if you are not tracking software releases, you can leave the list
of "releases" empty, and organization by release will be turned off. The
fields for areas and issue types come pre-configured with simple values that
presume you are tracking software bugs. You can modify these to suit your needs.

If a repository URL is provided, revision numbers will automatically be
hyperlinked when included in Issue descriptions and comments.

After creating the Tracker, use the "state" menu to open it for submissions.
Available workflow states are:

- Open: Anonymous users can view and submit issues
- Restricted: Anonymous users can view, but only members can submit
- Protected: Only members can view and submit
- Closed: Tracker is closed to submissions 

The Tracker front page includes:

- Issue search (as well as link to Advanced Search)
- Issue Logs link (view all Tracker activity)
- Watch This Tracker / Stop Watching This Tracker button to enable/disable notifications
- Browse Issues by release, state, area or tag
- "My Submitted Issues" listing
- "Orphaned Issues" listing (unassigned Issues)
- "Issues Assigned to Me" 


Issue Usage
-----------

Once you have set up the Tracker, Issues (tickets) can be created within the
Tracker. Who can create them depends on the Tracker's state (see list above).
Issues contain:

- Title
- Release (version Issue was found in)
- Details (description)
- Steps to Reproduce
- Related Issues (select from existing Issues within the Tracker)
- Area, Type and Severity
- Target Release (for fix)
- Contact Email
- Requested By Date
- Ticket Owner (Assignee)
- Watchers
- Subjects (Tags) 

Once an Issue is created:

- Attachments can be added to the Issue
- Responses can be added
- When adding a response as a tracker manager, you can change the state, importance or assignment of an issue.

Issues have the following workflow:

.. image:: http://www.sixfeetup.com/logos/issue-workflow.png
   :height: 756
   :width: 553
   :alt: Issue Workflow
   :align: left


Email Notification
------------------

If email notification is enabled in the Tracker setup, the following conditions will exist.

- If a mailing list was provided in the Tracker setup, members of the list will also be notified.
- All listed Tracker Assignees automatically become Tracker Watchers when the tracker is created.
- A Ticket Owner (assignee assigned to an issue) automatically becomes an Issue Watcher for that issue. 

+--------------------------+-------------+----------------+----------------+
| User                     | New Issue   | Issue Response | Issue Resolved |
+==========================+=============+================+================+
| **Tracker Watcher**      | X           | X              | X              |
+--------------------------+-------------+----------------+----------------+
| **Tracker Mailing List** | X           | X              | X              |
+--------------------------+-------------+----------------+----------------+
| **Issue Watcher**        |             | X*             | X              |
+--------------------------+-------------+----------------+----------------+
| **Issue Submitter**      |             |                | X              |
+--------------------------+-------------+----------------+----------------+
| **Member**               |             |                | X              |
+--------------------------+-------------+----------------+----------------+


`*` except responses they post 

For additional mail functionality, also see `poi.receivemail` and
`poi.maildefaults`


Roles and Permissions
---------------------

Poi adds 3 Roles to the defaults in Plone. Roles honor inheritance.
Note that some of these permissions will change based on the
state of the tracker.

+-----------------------------+-------------+----------------+----------------+----------------+------------+
|                             | Anonymous   | Member         | Manager        | TrackerManager | Technician |
+=============================+=============+================+================+================+============+
| Add Tracker                 |             |                | X              |                |            |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Manage Tracker              |             |                | X              | X              |            |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Add Issue                   |  X          | X              | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Add Response                |  X          | X              | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Edit Response               |             |                | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Upload Attachment           |             | X              | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Modify Issue Severity       |             |                | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Modify Issue Assignment     |             |                | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Modify Issue State          |             |                | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Modify Issue Tags           |             |                | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Modify Issue Watchers       |             |                | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Modify Issue Target Release |             |                | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+
| Modify Related Issues       |  X          | X              | X              | X              | X          |
+-----------------------------+-------------+----------------+----------------+----------------+------------+



Credits
=======

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
