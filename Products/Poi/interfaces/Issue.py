# File: Issue.py
# 
# Copyright (c) 2006 by Copyright (c) 2004 Martin Aspeli
# Generator: ArchGenXML Version 1.4.1 svn/devel 
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

class Issue(Base):
    """
    Marker interface for FirePoi Issues
    """

    #Methods

    def toggleWatching():
        """
        Add or remove the current authenticated member from the list of
        watchers.
        """
        
        pass



    def isWatching():
        """
        Determine if the current user is watching this issue or not.
        """
        
        pass



    def getLastModificationUser():
        """
        Get the user id of the user who last modified the issue, either
        by
        creating, editing or adding a response to it. May return None if
        the user is unknown.
        """
        
        pass


# end of class Issue

