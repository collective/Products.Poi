# File: Tracker.py
# 
# Copyright (c) 2005 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML  
#            http://plone.org/products/archgenxml
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#
__author__  = '''Martin Aspeli <optilude@gmx.net>'''
__docformat__ = 'plaintext'




from Interface import Base

class Tracker(Base):
    """
    Interface for FirePoi trackers. Trackers can display their
    contained issues filtered by workflow state and category.
    """

    #Methods

    def getFilteredIssues(criteria, **kwargs):
        """
        Get the contained issues according to the given criteria.
        
        Valid keys are:
        
        area -- An area or list of areas
        issueType -- An issue type or list of issue types
        severity -- A severity or list of severities
        release -- A release or list of releases
        responsible -- A resonsible manager or list of managers
        tags -- An issue tag or list of issue tags
        creator -- The user name of the issue submitter
        text -- Free text search
        sort_on -- Index to sort on
        """

        pass



    def isUsingReleases():
        """
        Find out if this tracker is organising issues by release or not.
        """
        
        pass



    def getNotificationEmailAddresses():
        """
        Upon activity for the given issue, get the list of email
        addresses
        to which notifications should be sent. May return an empty list
        if notification is turned off.
        """
        
        pass



    def sendNotificationEmail(addresses,subject,text):
        """
        Send a notification email
        """
        
        pass



    def getTagsInUse():
        """
        Get a list of the issue tags in use in this tracker.
        """
        
        pass


# end of class Tracker

