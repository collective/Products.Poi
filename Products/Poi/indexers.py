from collective import dexteritytextindexer
from zope.component import adapts
from zope.interface import implementer

from Products.Poi.adapters import IResponseContainer
from Products.Poi.interfaces import IIssue


@implementer(dexteritytextindexer.IDynamicTextIndexExtender)
class ResponseIndexer(object):
    adapts(IIssue)

    def __init__(self, context):
            self.context = context

    def __call__(self):
        issue = self.context
        terms = []
        container = IResponseContainer(issue)
        for response in container:
            if response is None:
                continue
            terms.append(response.text)
        return ' '.join(terms)
