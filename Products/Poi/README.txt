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

Feedback is very welcome. Yes, we will have a Poi tracker for Poi soon. :)

Installation and dependencies

  Poi requires Plone 2.1 and ArchAddOn, currently from svn. When Poi is 
released, a release of ArchAddOn will be made as well. For PloneSoftwareCenter
integration, PloneSoftwareCenter 1.0beta7 (currently from the
plone2.1-integration branch) is required.

Install using Add/Remove Products as normal. If you want PloneSoftwareCenter
configuration to be automatically configured, install PSC *first*.

Usage

 Add a Tracker, and use the "state" menu to open it for submissions. 
 
The tracker front pages allows you to browse for issues by release, state or 
topic, as well as search for issues. Note that if you are not tracking software 
releases, you can leave the list of "releases" empty, and organisation by 
release will be turned off. The fields for topics and category come 
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

 Poi is maintained using ArchGenXML (current svn or at least 1.4beta2), with
a Poseidon model found in the model/ directory. Let's keep it that way.

Credits

 o Design and development by Martin Aspeli <optilude@gmx.net>
 
 o Icons by Vidar Andersen, Black Tar, originally created for CMFCollector.
