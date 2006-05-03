Poi: A friendly issue tracker

 by Martin Aspeli <optilude@gmx.net>
 Released under the GNU General Public License, version 2
 
Poi is an issue tracker product for Plone. It has three overarching aims:

- Work with, not against Plone, and use Plone 2.1 features.

- Be simple and attractive whilst providing the most commonly needed issue
tracking functionality.

- Optionally integrate with the PloneSoftwareCenter to allow individual products
to have their own issue trackers

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

Please note two **very important** things:

- If you upgrade Poi, you're likely to have to make this change again!
 
- If you have issue text fields, and you have contentmigration installed, and
text/html is not in the list of available MIME types above, then a migration 
will be run which will turn all your HTML fields into plain text! If this
happens to you by accident - don't complain, you should've had a backup :)

Installation and dependencies

  Poi requires:
  
    - Plone 2.1.2+
    - DataGridField (*)
    - AddRemoveWidget
    - intelligenttext
    
    - For migration from versions before 1.0b2, contentmigration is required.
    
    - For PloneSoftwareCenter integration, PloneSoftwareCenter 1.0beta7 
        (currentlyfrom the plone2.1-integration branch) is required.

(*) NOTE: Before version 1.0 beta 2, ArchAddOn was required instead of
DataGridField. 

For new installations, install using Add/Remove Products as normal. If you want
PloneSoftwareCenter configuration to be automatically configured, install PSC
*first*. 

Upgrading

If you had a version prior to 1.0 beta 2 installed, you must run migrations. 
This is automatic, but you need to install the 'contentmigration' product. This 
can be found at

    https://svn.plone.org/svn/collective/contentmigration/trunk
    
It is also bundled with the release tarball. Simply drop the 'contentmigration'
product into your Products/ folder and re-install Poi from the Add/Remove 
Products control panel or portal_quickinstaller in the ZMI.

After any upgrade (and after you have run migrations!), run an Archetypes schema
update, by going to 'archetype_tool' in the ZMI, selecting the 'Update Schema'
tab, selecting all the 'Poi.*' types, and clicking 'Update schema'. It's
probably a good idea to choose 'All objects' from the drop-down as well,
although this will take slightly longer.

If you get errors about things being 'Missing', try to update your catalog,
by going to portal_catalog in the ZMI, clicking the Advanced tab, and then
the 'Update catalog' button.

If you do not have any old Poi trackers around, you do not need to run 
migrations.

Usage

 Add a Tracker, and use the "state" menu to open it for submissions. 
 
The tracker front pages allows you to browse for issues by release, state or 
area, as well as search for issues. Note that if you are not tracking software 
releases, you can leave the list of "releases" empty, and organisation by 
release will be turned off. The fields for areas and issue types come 
pre-configured with simple values that presume you are tracking software bugs. 
You can change these to whatever you want. 

Once you have set up the tracker, add Issues inside, and Responses inside
Issues. Anyone can add responses to issues with the default workflow. Responses
from tracker managers (as configured on the root tracker object) and the 
original submitter are colour coded to make them easier to pick out. Use the
"state" drop-down to change the current status of an issue.

If email notification is enabled in the root tracker object, managers will
get an email when there are new issues and responses, optionally via a mailing
list. Issue submittes will also get emails upon issue responses. Additionally,
when an issue is marked as "resolved" by a tracker manager, the submitter will
receive an email asking him or her to mark the issue as confirmed closed.

To use with the PloneSoftwareCenter, install PSC and *then* install Poi. This
will ensure PoiPscTracker is added to the list of allowed content types in
portal_types/PSCProject. You can then add Trackers inside a project in the
software center. The trackers will function in the same way as regular trackers,
but will use releases from the software center project instead of a manually
defined list.

Contributing

 Poi is maintained using ArchGenXML (current svn or at least version 1.4), with
a Poseidon model found in the model/ directory. Let's keep it that way.  

If you have contributed to Poi in some fashion, be sure to add yourself to 
the Credits section!

Credits

 o Design and development by Martin Aspeli <optilude@gmx.net>

 o Bug fixes and general critiquing by Rocky Burt <rocky@serverzen.com>

 o Icons by Vidar Andersen, Black Tar, originally created for CMFCollector.
