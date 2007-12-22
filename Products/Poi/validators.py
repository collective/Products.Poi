"""Validator for DataGridFields.

For the DataGridFields, making them required is not enough as there is
always a hidden entry.  So we check if there is least one normal entry
and one hidden entry, so more than 1 entry in total.
"""

from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator


class DataGridValidator:
    """Validate as True when having at least one DataGrid item.
    """

    __implements__ = IValidator

    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        try:
            length = len(value) - 1
        except TypeError:
            return ("Validation failed(%s): cannot calculate length "
                    "of %s.""" % (self.name, value))
        except AttributeError:
            return ("Validation failed(%s): cannot calculate length "
                    "of %s.""" % (self.name, value))
        if length < 1:
            return ("Validation failed(%s): Need at least one entry."
                    % self.name)
        return True


isDataGridFilled = DataGridValidator(
    'isDataGridFilled', title='DataGrid Filled',
    description='The DataGridField must have at least one entry.')
validation.register(isDataGridFilled)
