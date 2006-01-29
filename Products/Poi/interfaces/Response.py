# File: Response.py
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

class Response(Base):
    """
    Marker interface for FirePoi issue responses
    """

    #Methods

    def setNewIssueState(transition):
        """
        Set a new review state for the parent issue, by executing
        the given transition.
        """
        
        pass



    def setNewSeverity(severity):
        """
        Set a new issue severity for the parent issue
        """
        
        pass



    def setNewTargetRelease(release):
        """
        Set a new target release for the parent issue
        """
        
        pass



    def setNewResponsibleManager(manager):
        """
        Set a new responsible manager for the parent issue
        """
        
        pass



    def getIssueChanges():
        """
        Get a list of changes this response has made to the issue.
        Contains dicts with keys:
        
            id: The name of the field that was changed
            name: A human readable name
            before: The state of the field before
            after: The new state of the field
        """
        
        pass


# end of class Response

