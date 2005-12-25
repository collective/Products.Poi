from Products.PortalTransforms.interfaces import itransform
import re

# This is taken from Ploneboard's text_to_hyperlink, but lives here until it can 
# be factored out so that we avoid a direct dependency on Ploneboard.

class IntelligentPlainText:
    """Transform which replaces urls and email into hyperlinks"""

    __implements__ = itransform

    __name__ = "intelligent_plain_text"
    output = "text/plain"

    def __init__(self, name=None, inputs=('text/plain',)):
        self.config = { 'inputs' : inputs, }
        self.config_metadata = {
            'inputs' : ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name
            
    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        urlchars = r'[A-Za-z0-9/:@_%~#=&\.\-\?]+'
        url = r'["=]?((http|ftp|https):%s)' % urlchars
        emailRegexp = r'["=]?(\b[A-Z0-9._%-]+@[A-Z0-9._%-]+\.[A-Z]{2,4}\b)'
        
        regexp = re.compile(url, re.I|re.S)
        def replaceURL(match):
            url = match.groups()[0]
            return '<a href="%s">%s</a>' % (url, url)
        text = regexp.subn(replaceURL, orig)[0]
        
        regexp = re.compile(emailRegexp, re.I|re.S)
        def replaceEmail(match):
            url = match.groups()[0]
            return '<a href="mailto:%s">%s</a>' % (url, url)
        text = regexp.subn(replaceEmail, text)[0]
    
        data.setData(text)
        return data

def register():
    return IntelligentPlainText()
