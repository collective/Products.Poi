try:
    from Products.validation.interfaces.IValidator import IValidator
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
    from interfaces.IValidator import IValidator
    del sys, os
import re

class TimeEstimateValidator:
    __implements__ = IValidator
    
    format = re.compile(r"\s*(\d+d)?\s*(\d+h)?\s*(\d+m)?\s*")

    def __init__(self,
                 name,
                 title='TimeEstimateValidator',
                 description='Validates for [%dd] [%dh] [%dm]'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        
        m = self.format.match(value)
        
        if reduce(lambda x, y: x or y, m.groups()):
            return True
        else:
            return('Format: $Nd $Nh $Nm')

from Products.validation import validation
validation.register(TimeEstimateValidator('timeestimate'))
