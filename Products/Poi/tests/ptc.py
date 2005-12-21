from Testing import ZopeTestCase

from DateTime import DateTime

# Make the boring stuff load quietly
ZopeTestCase.installProduct('CMFCore', quiet=1)
ZopeTestCase.installProduct('CMFDefault', quiet=1)
ZopeTestCase.installProduct('CMFCalendar', quiet=1)
ZopeTestCase.installProduct('CMFTopic', quiet=1)
ZopeTestCase.installProduct('DCWorkflow', quiet=1)
ZopeTestCase.installProduct('CMFHelpIcons', quiet=1)
ZopeTestCase.installProduct('CMFQuickInstallerTool', quiet=1)
ZopeTestCase.installProduct('CMFFormController', quiet=1)
ZopeTestCase.installProduct('GroupUserFolder', quiet=1)
ZopeTestCase.installProduct('ZCTextIndex', quiet=1)
ZopeTestCase.installProduct('TextIndexNG2', quiet=1)
ZopeTestCase.installProduct('SecureMailHost', quiet=1)
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('Archetypes')
ZopeTestCase.installProduct('PortalTransforms', quiet=1)
ZopeTestCase.installProduct('MimetypesRegistry', quiet=1)
ZopeTestCase.installProduct('Five', quiet=1)
ZopeTestCase.installProduct('DataGridField', quiet=1)
ZopeTestCase.installProduct('contentmigrations', quiet=1)

ZopeTestCase.installProduct('Poi')

from Products.PloneTestCase import PloneTestCase

PRODUCTS = ['Poi']

PloneTestCase.setupPloneSite(products=PRODUCTS)


class PoiTestCase(PloneTestCase.PloneTestCase):

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()

    # Taken from CMFPlone/tests/testMemberDataTool
    def addMember(self, username, fullname, email, roles, last_login_time):
        self.portal.portal_membership.addMember(username, 'secret', roles, [])
        member = self.portal.portal_membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def createTracker(self, folder, id, title='', description='',
                        availableAreas=({'id' : 'ui', 'title' : 'User interface', 'description' : 'User interface issues'}, {'id' : 'functionality', 'title' : 'Functionality', 'description' : 'Issues with the basic functionality'}, {'id' : 'process', 'title' : 'Process', 'description' : 'Issues relating to the development process itself'}),
                        availableIssueTypes=({'id' : 'bug', 'title' : 'Bug', 'description' : 'Functionality bugs in the software'}, {'id' : 'feature', 'title' : 'Feature', 'description' : 'Suggested features'}, {'id' : 'patch', 'title' : 'Patch', 'description' : 'Patches to the software'}),
                        availableSeverities=['Critical', 'Important', 'Medium', 'Low'],
                        defaultSeverity='Medium',
                        availableReleases=['2.0', '1.0'],
                        managers=[],
                        sendNotificationEmails=False,
                        mailingList=''):
        """Create a new tracker in the given folder"""
        self.setRoles(['Manager'])
        folder.invokeFactory('PoiTracker', id)
        tracker = getattr(folder, id)
        tracker.setTitle(title)
        tracker.setDescription(description)
        tracker.setAvailableAreas(availableAreas)
        tracker.setAvailableIssueTypes(availableIssueTypes)
        tracker.setAvailableSeverities(availableSeverities)
        tracker.setDefaultSeverity(defaultSeverity)
        tracker.setAvailableReleases(availableReleases)
        tracker.setManagers(managers)
        tracker.setSendNotificationEmails(sendNotificationEmails)
        tracker.setMailingList(mailingList)
        tracker.reindexObject()
        self.setRoles(['Member'])
        
        return tracker

    def createIssue(self, tracker, title='An issue', 
                    overview='Something is wrong', release='(UNASSIGNED)', 
                    area='ui', issueType='bug', severity='Medium', 
                    targetRelease='(UNASSIGNED)',
                    details='', steps=(), attachment=None, 
                    contactEmail='submitter@domain.com',
                    watchers=(),
                    tags=(),
                    responsibleManager='(UNASSIGNED)'):
        """Create an issue in the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        newId = self.portal.generateUniqueId('PoiIssue')
        oldIds = tracker.objectIds()
        tracker.invokeFactory('PoiIssue', newId)
        issue = getattr(tracker, newId)
        issue.setTitle(title)
        issue.setDescription(overview)
        issue.setRelease(release)
        issue.setArea(area)
        issue.setIssueType(issueType)
        issue.setSeverity(severity)
        issue.setTargetRelease(targetRelease)
        issue.setDetails(details)
        issue.setSteps(steps)
        issue.setAttachment(attachment)
        issue.setContactEmail(contactEmail)
        issue.setWatchers(watchers)
        issue.setSubject(tags)
        issue.setResponsibleManager(responsibleManager)
        self.portal.portal_workflow.doActionFor(issue, 'post')
        issue._renameAfterCreation()
        issue.reindexObject()
        return issue

    def createResponse(self, issue, text='Respnse text', issueTransition='',
                        newSeverity=None, newTargetRelease=None,
                        newResponsibleManager=None, attachment=None):
        """Create a response to the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        newId = self.portal.generateUniqueId('PoiResponse')
        issue.invokeFactory('PoiResponse', newId)
        response = getattr(issue, newId)
        response.setResponse(text)
        response.setNewIssueState(issueTransition)
        response.setNewSeverity(newSeverity)
        response.setNewTargetRelease(newTargetRelease)
        response.setNewResponsibleManager(newResponsibleManager)
        response.setAttachment(attachment)
        self.portal.portal_workflow.doActionFor(response, 'post')
        response._renameAfterCreation()
        response.reindexObject()
        issue.updateResponses()
        return response