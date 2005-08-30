from Testing import ZopeTestCase

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

    def createTracker(self, folder, id, title='', description='',
                        availableTopics=['ui | User interface | User interface issues', 'functionality | Functionality| Issues with the basic functionality', 'process | Process | Issues relating to the development process itself'],
                        availableCategories=['bug | Bug | Functionality bugs in the software', 'feature | Feature | Suggested features', 'patch | Patch | Patches to the software'],
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
        tracker.setAvailableTopics(availableTopics)
        tracker.setAvailableSeverities(availableSeverities)
        tracker.setDefaultSeverity(defaultSeverity)
        tracker.setAvailableReleases(availableReleases)
        tracker.setManagers(managers)
        tracker.setSendNotificationEmails(sendNotificationEmails)
        tracker.setMailingList(mailingList)
        self.setRoles(['Member'])
        return tracker

    def createIssue(self, tracker, title='An issue', 
                    overview='Something is wrong', release='(UNASSIGNED)', 
                    topic='ui', category='bug', severity='Medium', 
                    details='', steps=(), attachment=None, 
                    contactEmail='submitter@domain.com',
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
        issue.setTopic(topic)
        issue.setCategory(category)
        issue.setSeverity(severity)
        issue.setDetails(details)
        issue.setSteps(steps)
        issue.setAttachment(attachment)
        issue.setContactEmail(contactEmail)
        issue.setResponsibleManager(responsibleManager)
        self.portal.portal_workflow.doActionFor(issue, 'post')
        issue._renameAfterCreation()
        return issue

    def createResponse(self, issue, text='Respnse text', issueTransition='',
                        attachment=None):
        """Create a response to the given tracker, and perform workflow and
        rename-after-creation initialisation"""
        newId = self.portal.generateUniqueId('PoiResponse')
        issue.invokeFactory('PoiResponse', newId)
        response = getattr(issue, newId)
        response.setResponse(text)
        response.setNewIssueState(issueTransition)
        response.setAttachment(attachment)
        self.portal.portal_workflow.doActionFor(response, 'post')
        response._renameAfterCreation()
        return response